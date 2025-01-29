from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from classes.models import Class
from learners.models import Learner
from .models import CustomUser, UserActivity
from .forms import CustomUserCreationForm, CustomUserChangeForm, UserProfileForm, ChangePasswordForm
from .mixins import SupervisorRequiredMixin
from django.db.models import Max, Q as models
from django.contrib import messages
from django.contrib.auth.forms import SetPasswordForm
import csv
from django.http import HttpResponse
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import View

class UserListView(SupervisorRequiredMixin, ListView):
    model = CustomUser
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        queryset = CustomUser.objects.all()
        
        # Search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(username__icontains=search_query) |
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(email__icontains=search_query)
            )
        
        # Role filter
        role = self.request.GET.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Status filter
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('username')

class UserCreateView(SupervisorRequiredMixin, CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'users/user_create.html'
    success_url = reverse_lazy('users:list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, 
            _('Ο χρήστης δημιουργήθηκε με επιτυχία.'),
            extra_tags='success user_created'
        )
        return response

class UserUpdateView(SupervisorRequiredMixin, SuccessMessageMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'users/user_form.html'
    success_url = reverse_lazy('users:list')
    success_message = _("Ο χρήστης ενημερώθηκε με επιτυχία.")

class UserPasswordResetView(SupervisorRequiredMixin, UpdateView):
    model = CustomUser
    template_name = 'users/password_reset.html'
    form_class = SetPasswordForm
    success_url = reverse_lazy('users:list')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.get_object()
        if 'instance' in kwargs:
            del kwargs['instance']
        return kwargs
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, _('Ο κωδικός άλλαξε με επιτυχία.'))
        return response

class UserDeleteView(SupervisorRequiredMixin, DeleteView):
    model = CustomUser
    template_name = 'users/user_confirm_delete.html'
    success_url = reverse_lazy('users:list')
    
    def get_queryset(self):
        # Prevent deletion of supervisors unless by superuser
        qs = super().get_queryset()
        if not self.request.user.is_superuser:
            qs = qs.exclude(role='supervisor')
        return qs
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(request, _('Ο χρήστης διαγράφηκε με επιτυχία.'))
        return response

class ManagementDashboardView(SupervisorRequiredMixin, TemplateView):
    template_name = 'management/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_users_count'] = CustomUser.objects.filter(is_active=True).count()
        context['classes_count'] = Class.objects.count()
        context['learners_count'] = Learner.objects.count()
        
        # Count pending evaluations (3-month and 6-month overdue)
        from datetime import datetime, timedelta
        from django.db.models import Max
        
        today = datetime.now().date()
        three_months_ago = today - timedelta(days=90)
        six_months_ago = today - timedelta(days=180)
        
        learners_needing_evaluation = Learner.objects.annotate(
            last_3month=Max('evaluations__evaluation_date', 
                          filter=models.Q(evaluations__evaluation_type='3month')),
            last_6month=Max('evaluations__evaluation_date', 
                          filter=models.Q(evaluations__evaluation_type='6month'))
        ).filter(
            models.Q(last_3month__lt=three_months_ago) | 
            models.Q(last_3month__isnull=True) |
            models.Q(last_6month__lt=six_months_ago) | 
            models.Q(last_6month__isnull=True)
        )
        
        context['pending_evaluations_count'] = learners_needing_evaluation.count()
        return context 

class UserActivityView(SupervisorRequiredMixin, ListView):
    model = UserActivity
    template_name = 'users/user_activity.html'
    context_object_name = 'activities'
    paginate_by = 20

    def get_queryset(self):
        queryset = UserActivity.objects.select_related('user', 'performed_by')
        
        # Filter by user
        user_id = self.request.GET.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
            
        # Filter by action
        action = self.request.GET.get('action')
        if action:
            queryset = queryset.filter(action=action)
            
        return queryset.order_by('-timestamp')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['all_users'] = CustomUser.objects.all().order_by('first_name', 'last_name')
        context['action_choices'] = UserActivity.ACTION_CHOICES
        return context 

class ExportUserActivityView(SupervisorRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Create the HttpResponse object with CSV header
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="user_activity_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        
        # Create CSV writer
        writer = csv.writer(response)
        writer.writerow(['Ημερομηνία/Ώρα', 'Χρήστης', 'Ενέργεια', 'Από', 'IP'])
        
        # Get filtered queryset
        activities = UserActivity.objects.select_related('user', 'performed_by')
        
        # Apply filters
        user_id = request.GET.get('user')
        if user_id:
            activities = activities.filter(user_id=user_id)
            
        action = request.GET.get('action')
        if action:
            activities = activities.filter(action=action)
        
        # Write data
        for activity in activities:
            writer.writerow([
                activity.timestamp.strftime('%d/%m/%Y %H:%M:%S'),
                activity.user.get_full_name() or activity.user.username,
                activity.get_action_display(),
                activity.performed_by.get_full_name() if activity.performed_by else 'Σύστημα',
                activity.ip_address or '-'
            ])
        
        return response 

class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_form'] = UserProfileForm(instance=self.request.user)
        context['password_form'] = ChangePasswordForm(user=self.request.user)
        context['recent_activities'] = UserActivity.objects.filter(
            user=self.request.user
        ).order_by('-timestamp')[:10]
        return context

class ProfileUpdateView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            request.user.log_activity('profile_update')
            messages.success(request, _('Το προφίλ ενημερώθηκε με επιτυχία.'))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        
        return redirect('users:profile')

class ChangePasswordView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = ChangePasswordForm(request.user, request.POST)
        if form.is_valid():
            request.user.set_password(form.cleaned_data['new_password1'])
            request.user.save()
            request.user.log_activity('password_change')
            messages.success(request, _('Ο κωδικός άλλαξε με επιτυχία.'))
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        
        return redirect('users:profile') 