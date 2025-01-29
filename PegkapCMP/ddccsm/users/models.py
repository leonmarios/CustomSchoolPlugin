from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('supervisor', _('Επόπτης')),
        ('teacher', _('Εκπαιδευτικός')),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='teacher',
        verbose_name=_('Ρόλος')
    )

    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='custom_user_set',
        related_query_name='custom_user',
    )

    def is_supervisor(self):
        return self.role == 'supervisor'

    def log_activity(self, action, performed_by=None):
        UserActivity.objects.create(
            user=self,
            action=action,
            performed_by=performed_by or self
        )

    class Meta:
        verbose_name = _('Χρήστης')
        verbose_name_plural = _('Χρήστες')

class UserActivity(models.Model):
    ACTION_CHOICES = [
        ('login', _('Σύνδεση')),
        ('logout', _('Αποσύνδεση')),
        ('password_change', _('Αλλαγή Κωδικού')),
        ('password_reset', _('Επαναφορά Κωδικού')),
        ('profile_update', _('Ενημέρωση Προφίλ')),
        ('account_created', _('Δημιουργία Λογαριασμού')),
        ('account_deactivated', _('Απενεργοποίηση Λογαριασμού')),
        ('account_activated', _('Ενεργοποίηση Λογαριασμού')),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='activities')
    performed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='performed_activities')
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = _('Δραστηριότητα Χρήστη')
        verbose_name_plural = _('Δραστηριότητες Χρηστών')
        ordering = ['-timestamp']

    def __str__(self):
        return f'{self.user.username} - {self.get_action_display()}' 