from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView, FormView, View, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db import transaction, connection
from .models import Learner, FormField, LearnerFile, Evaluation, SocialHistory, FamilyMember
from .forms import LearnerForm, ImportForm, UserForm, EvaluationForm, LearnerSelectForm, FamilyMemberForm, SocialHistoryForm
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.db.models import Q
from import_export.formats import base_formats
from .resources import LearnerResource
from .services import LearnerStatistics, AuditLogger
from django.contrib.auth import get_user_model
from .mixins import AdminRequiredMixin, StaffRequiredMixin, LearnerPermissionMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from users.mixins import SupervisorRequiredMixin
from django.utils import timezone

User = get_user_model()

# Create your views here.

class LearnerFileView(LoginRequiredMixin, View):
    def get(self, request, pk, field_name):
        learner = get_object_or_404(Learner, pk=pk)
        try:
            file_obj = learner.get_file_for_field(field_name)
            if file_obj:
                response = HttpResponse(file_obj.file, content_type='application/octet-stream')
                response['Content-Disposition'] = f'attachment; filename="{file_obj.filename}"'
                return response
        except:
            raise Http404("File not found")

class LearnerCreateView(SupervisorRequiredMixin, CreateView):
    model = Learner
    form_class = LearnerForm
    template_name = 'learners/learner_form.html'
    success_url = reverse_lazy('learners:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, 
            _('Ο ωφελούμενος δημιουργήθηκε με επιτυχία.'),
            extra_tags='success learner_created'
        )
        return response

class LearnerUpdateView(SupervisorRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Learner
    form_class = LearnerForm
    template_name = 'learners/learner_form.html'
    success_url = reverse_lazy('learners:list')
    success_message = _("Ο ωφελούμενος ενημερώθηκε με επιτυχία.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        fields_by_section = {}
        form_fields = FormField.objects.filter(is_active=True).order_by('order')
        
        for field in form_fields:
            if field.section not in fields_by_section:
                fields_by_section[field.section] = []
            fields_by_section[field.section].append(field.name)
            
        context['fields_by_section'] = fields_by_section
        context['additional_guardian_emails'] = self.object.additional_guardian_emails
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Log the changes
        AuditLogger.log_action(
            user=self.request.user,
            action='update',
            instance=self.object,
            ip_address=self.request.META.get('REMOTE_ADDR')
        )
        
        messages.success(self.request, _('Ο ωφελούμενος ενημερώθηκε με επιτυχία.'))
        return response

class LearnerListView(LoginRequiredMixin, LearnerPermissionMixin, ListView):
    model = Learner
    template_name = 'learners/learner_list.html'
    context_object_name = 'learners'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Learner.objects.all()
        ordering = self.request.GET.get('order_by', 'id')  # Default sort by id
        direction = self.request.GET.get('direction', 'asc')  # Default ascending
        
        if direction == 'desc':
            ordering = f'-{ordering}'
            
        return queryset.order_by(ordering)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['is_active_filter'] = self.request.GET.get('active', '')
        context['section_filter'] = self.request.GET.get('section', '')
        context['current_order'] = self.request.GET.get('order_by', 'id')
        context['current_direction'] = self.request.GET.get('direction', 'asc')
        return context

class LearnerDetailView(LoginRequiredMixin, DetailView):
    model = Learner
    template_name = 'learners/learner_detail.html'
    context_object_name = 'learner'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['evaluations'] = self.object.evaluations.all().select_related('evaluator')
        return context

class LearnerDeleteView(SupervisorRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Learner
    template_name = 'learners/learner_confirm_delete.html'
    success_url = reverse_lazy('learners:list')
    success_message = _("Ο ωφελούμενος διαγράφηκε με επιτυχία.")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        # Log the deletion
        AuditLogger.log_action(
            user=request.user,
            action='delete',
            instance=self.object,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        messages.success(request, 'Ο ωφελούμενος διαγράφηκε με επιτυχία.')
        return super().delete(request, *args, **kwargs)

class ImportExportMixin:
    resource_class = LearnerResource
    
    def get_resource(self):
        return self.resource_class()

class ImportLearnersView(LoginRequiredMixin, PermissionRequiredMixin, ImportExportMixin, FormView):
    template_name = 'learners/import.html'
    form_class = ImportForm
    success_url = reverse_lazy('learners:list')
    permission_required = 'learners.add_learner'

    def form_valid(self, form):
        import_file = form.cleaned_data['import_file']
        import_format = form.cleaned_data['import_format']
        
        try:
            dataset = import_format.create_dataset(import_file)
            result = self.get_resource().import_data(dataset, 
                                                   dry_run=False,
                                                   raise_errors=True,
                                                   collect_failed_rows=True)
            
            if result.has_errors() or result.has_validation_errors():
                messages.error(self.request, 
                             _('Υπήρξαν σφάλματα κατά την εισαγωγή. Ελέγξτε τα δεδομένα σας.'))
            else:
                messages.success(self.request, 
                               _(f'Επιτυχής εισαγωγή {result.total_rows} εγγραφών.'))
                
        except Exception as e:
            messages.error(self.request, str(e))
            
        return super().form_valid(form)

class ExportLearnersView(LoginRequiredMixin, PermissionRequiredMixin, ImportExportMixin, View):
    permission_required = 'learners.view_learner'

    def get(self, request, *args, **kwargs):
        file_format = request.GET.get('format', 'xlsx')
        
        if file_format not in ['xlsx', 'csv']:
            file_format = 'xlsx'
            
        dataset = self.get_resource().export()
        
        if file_format == 'xlsx':
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="learners.xlsx"'
            dataset.xlsx.write(response)
        else:
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename="learners.csv"'
            response.write(dataset.csv)
            
        return response

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'learners/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stats = LearnerStatistics()
        context['statistics'] = stats.get_all_statistics()
        return context

class UserManagementView(LoginRequiredMixin, AdminRequiredMixin, ListView):
    model = User
    template_name = 'learners/user_list.html'
    context_object_name = 'users'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['groups'] = Group.objects.all()
        return context

class UserCreateView(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = 'learners/user_form.html'
    success_url = reverse_lazy('learners:user_list')

class UserUpdateView(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'learners/user_form.html'
    success_url = reverse_lazy('learners:user_list')

def evaluation_create(request, learner_id):
    print(f"Accessing evaluation_create with learner_id: {learner_id}")
    print(f"Available learner IDs: {list(Learner.objects.values_list('id', flat=True))}")
    
    learner = get_object_or_404(Learner, pk=learner_id)
    print(f"Found learner: {learner}")
    
    if request.method == 'POST':
        form = EvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.learner = learner
            evaluation.save()
            messages.success(request, 'Η αξιολόγηση δημιουργήθηκε με επιτυχία.')
            return HttpResponseRedirect(reverse('learners:detail', args=[learner_id]))
    else:
        # Prefill the date with today's date
        form = EvaluationForm(initial={
            'evaluation_date': timezone.now().date()
        })
    
    return render(request, 'learners/learner_evaluate.html', {
        'form': form,
        'learner': learner
    })

class EvaluationUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Evaluation
    form_class = EvaluationForm
    template_name = 'learners/evaluation_form.html'
    success_message = _("Η αξιολόγηση ενημερώθηκε με επιτυχία.")

    def get_success_url(self):
        return reverse_lazy('learners:detail', kwargs={'pk': self.object.learner.pk})

class EvaluationDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Evaluation
    template_name = 'learners/evaluation_confirm_delete.html'
    success_message = _("Η αξιολόγηση διαγράφηκε με επιτυχία.")

    def get_success_url(self):
        return reverse_lazy('learners:detail', kwargs={'pk': self.object.learner.pk})

class EvaluationListView(LoginRequiredMixin, ListView):
    model = Evaluation
    template_name = 'learners/evaluation_list.html'
    context_object_name = 'evaluations'
    paginate_by = 10

    def get_queryset(self):
        return Evaluation.objects.all().select_related('learner', 'evaluator').order_by('-evaluation_date')

class EvaluationCreateSelectView(LoginRequiredMixin, FormView):
    form_class = LearnerSelectForm
    template_name = 'learners/evaluation_select_learner.html'

    def form_valid(self, form):
        learner_id = form.cleaned_data['learner'].id
        return redirect('learners:evaluation_create', learner_id=learner_id)

class SocialHistoryUpdateView(UpdateView):
    model = SocialHistory
    form_class = SocialHistoryForm
    template_name = 'learners/social_history_form.html'

    def get_object(self):
        # Get the SocialHistory object for this learner
        return get_object_or_404(SocialHistory, learner_id=self.kwargs['pk'])

    def get_success_url(self):
        return reverse_lazy('learners:list')  # or wherever you want to redirect

class SocialHistoryCreateView(CreateView):
    model = SocialHistory
    form_class = SocialHistoryForm
    template_name = 'learners/social_history_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['debug_info'] = {
            'view_name': self.__class__.__name__,
            'learner_pk': self.kwargs.get('pk'),
            'form_exists': bool(context.get('form')),
            'template_name': self.template_name,
        }
        return context

    def form_valid(self, form):
        form.instance.learner_id = self.kwargs['pk']
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('learners:list')

class LearnerEvaluateView(DetailView):
    model = Learner
    template_name = 'learners/learner_evaluate.html'
    context_object_name = 'learner'
