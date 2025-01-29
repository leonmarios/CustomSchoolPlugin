from django.contrib.auth.mixins import UserPassesTestMixin, PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy

class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff or \
               self.request.user.groups.filter(name__in=['Administrators', 'Staff']).exists()

    def handle_no_permission(self):
        messages.error(self.request, 'Δεν έχετε δικαίωμα πρόσβασης σε αυτή τη σελίδα.')
        return redirect('learners:list')

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser or \
               self.request.user.groups.filter(name='Administrators').exists()

class LearnerPermissionMixin(PermissionRequiredMixin):
    login_url = reverse_lazy('login')

    def get_permission_required(self):
        """
        Override this method to customize permissions based on the view
        """
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return ['learners.change_learner']
        return ['learners.view_learner']

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            messages.error(self.request, 'Δεν έχετε τα απαραίτητα δικαιώματα για αυτή την ενέργεια.')
            return redirect('learners:list')
        return super().handle_no_permission() 