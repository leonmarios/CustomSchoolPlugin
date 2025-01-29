from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction, IntegrityError
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from .models import Class, ClassSchedule, TeacherAssignment
from .forms import ClassForm, TeacherAssignmentForm
from users.mixins import SupervisorRequiredMixin
from django.views import View
from django.template.loader import select_template

# Create your views here.

class ClassListView(LoginRequiredMixin, ListView):
    model = Class
    context_object_name = 'classes'
    template_name = 'classes/class_list.html'
    paginate_by = 10

class ClassDetailView(DetailView):
    model = Class
    template_name = 'classes/class_detail.html'
    context_object_name = 'class'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['weekdays'] = ClassSchedule.WEEKDAYS
        context['time_slots'] = ClassSchedule.TIME_SLOTS
        return context

class ClassCreateView(View):
    def get(self, request):
        form = ClassForm()
        
        # Create an empty grid structure
        schedule_grid = []
        for time_slot, time_display in ClassSchedule.TIME_SLOTS:
            row = {
                'time': time_display,
                'slots': []
            }
            for day_id, day_name in ClassSchedule.WEEKDAYS:
                row['slots'].append({
                    'day_id': day_id,
                    'time_slot': time_slot,
                    'activity': ''
                })
            schedule_grid.append(row)
        
        context = {
            'form': form,
            'weekdays': ClassSchedule.WEEKDAYS,
            'schedule_grid': schedule_grid,
        }
        
        return render(request, 'classes/class_form_simple.html', context)
    
    def post(self, request):
        form = ClassForm(request.POST)
        
        if form.is_valid():
            instance = form.save()
            
            # Create a set to track unique combinations
            schedule_entries = set()
            
            # Save schedule data
            for key, value in request.POST.items():
                if key.startswith('schedule-') and value:
                    _, day, time = key.split('-', 2)
                    entry_key = (instance.pk, int(day), time)
                    
                    # Only create if this combination doesn't exist
                    if entry_key not in schedule_entries:
                        schedule_entries.add(entry_key)
                        try:
                            ClassSchedule.objects.create(
                                class_instance=instance,
                                weekday=int(day),
                                time_slot=time,
                                activity=value
                            )
                        except IntegrityError:
                            # Skip if entry already exists
                            continue
            
            return redirect('classes:detail', pk=instance.pk)
        
        context = {
            'form': form,
            'weekdays': ClassSchedule.WEEKDAYS,
            'time_slots': ClassSchedule.TIME_SLOTS,
        }
        return render(request, 'classes/class_form_simple.html', context)

class ClassUpdateView(View):
    def get(self, request, pk):
        class_obj = get_object_or_404(Class, pk=pk)
        form = ClassForm(instance=class_obj)
        
        # Get all schedule entries
        schedule_entries = ClassSchedule.objects.filter(class_instance=class_obj)
        
        # Create a grid structure that matches the template
        schedule_grid = []
        for time_slot, time_display in ClassSchedule.TIME_SLOTS:
            row = {
                'time': time_display,
                'slots': []
            }
            for day_id, day_name in ClassSchedule.WEEKDAYS:
                entry = schedule_entries.filter(weekday=day_id, time_slot=time_slot).first()
                row['slots'].append({
                    'day_id': day_id,
                    'time_slot': time_slot,
                    'activity': entry.activity if entry else ''
                })
            schedule_grid.append(row)
        
        context = {
            'form': form,
            'object': class_obj,
            'weekdays': ClassSchedule.WEEKDAYS,
            'schedule_grid': schedule_grid,
        }
        
        return render(request, 'classes/class_form_simple.html', context)
    
    def post(self, request, pk):
        class_obj = get_object_or_404(Class, pk=pk)
        form = ClassForm(request.POST, instance=class_obj)
        
        if form.is_valid():
            instance = form.save()
            
            # Save schedule data
            ClassSchedule.objects.filter(class_instance=instance).delete()
            
            # Create a set to track unique combinations
            schedule_entries = set()
            
            for key, value in request.POST.items():
                if key.startswith('schedule-') and value:
                    _, day, time = key.split('-', 2)
                    entry_key = (instance.pk, int(day), time)
                    
                    # Only create if this combination doesn't exist
                    if entry_key not in schedule_entries:
                        schedule_entries.add(entry_key)
                        try:
                            ClassSchedule.objects.create(
                                class_instance=instance,
                                weekday=int(day),
                                time_slot=time,
                                activity=value
                            )
                        except IntegrityError:
                            # Skip if entry already exists
                            continue
            
            return redirect('classes:detail', pk=instance.pk)
        
        context = {
            'form': form,
            'object': class_obj,
            'weekdays': ClassSchedule.WEEKDAYS,
            'time_slots': ClassSchedule.TIME_SLOTS,
        }
        return render(request, 'classes/class_form_simple.html', context)

class ClassDeleteView(SupervisorRequiredMixin, SuccessMessageMixin, DeleteView):
    model = Class
    template_name = 'classes/class_confirm_delete.html'
    success_url = reverse_lazy('classes:list')
    success_message = _("Η τάξη διαγράφηκε με επιτυχία.")

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Το τμήμα διαγράφηκε με επιτυχία.')
        return super().delete(request, *args, **kwargs)

class TeacherAssignmentListView(LoginRequiredMixin, ListView):
    model = TeacherAssignment
    template_name = 'classes/teacher_assignment_list.html'
    context_object_name = 'assignments'

    def get_queryset(self):
        return TeacherAssignment.objects.select_related('teacher', 'class_group')

class TeacherAssignmentCreateView(SupervisorRequiredMixin, SuccessMessageMixin, CreateView):
    model = TeacherAssignment
    form_class = TeacherAssignmentForm
    template_name = 'classes/teacher_assignment_form.html'
    success_url = reverse_lazy('classes:teacher_assignment_list')
    success_message = _("Η ανάθεση δημιουργήθηκε με επιτυχία.")

class TeacherAssignmentUpdateView(SupervisorRequiredMixin, SuccessMessageMixin, UpdateView):
    model = TeacherAssignment
    form_class = TeacherAssignmentForm
    template_name = 'classes/teacher_assignment_form.html'
    success_url = reverse_lazy('classes:teacher_assignment_list')
    success_message = _("Η ανάθεση ενημερώθηκε με επιτυχία.")

class TeacherAssignmentDeleteView(SupervisorRequiredMixin, SuccessMessageMixin, DeleteView):
    model = TeacherAssignment
    template_name = 'classes/teacher_assignment_confirm_delete.html'
    success_url = reverse_lazy('classes:teacher_assignment_list')
    success_message = _("Η ανάθεση διαγράφηκε με επιτυχία.")
