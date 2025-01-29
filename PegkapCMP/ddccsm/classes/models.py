from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.conf import settings

class Activity(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Όνομα'))
    description = models.TextField(blank=True, verbose_name=_('Περιγραφή'))
    
    class Meta:
        verbose_name = _('Δραστηριότητα')
        verbose_name_plural = _('Δραστηριότητες')
        ordering = ['name']

    def __str__(self):
        return self.name

class Class(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Όνομα'))
    description = models.TextField(blank=True, verbose_name=_('Περιγραφή'))
    is_active = models.BooleanField(_('Ενεργό'), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    activities = models.ManyToManyField(
        Activity,
        related_name='classes',
        blank=True,
        verbose_name=_('Δραστηριότητες')
    )
    notes = models.TextField(
        blank=True,
        verbose_name=_('Σημειώσεις')
    )

    class Meta:
        verbose_name = _('Τμήμα')
        verbose_name_plural = _('Τμήματα')
        ordering = ['name']

    def __str__(self):
        return self.name

    def clean(self):
        if self.name:
            # Convert to lowercase for case-insensitive comparison
            name_lower = self.name.lower()
            existing = Class.objects.filter(name__iexact=self.name)
            
            # If this is an update, exclude the current instance
            if self.pk:
                existing = existing.exclude(pk=self.pk)
            
            if existing.exists():
                raise ValidationError({
                    'name': _('Υπάρχει ήδη τμήμα με αυτό το όνομα.')
                })

    @property
    def available_spots(self):
        # For now, just return the capacity until we implement students
        return self.capacity

    def save(self, *args, **kwargs):
        # Remove any message-sending code from here if it exists
        super().save(*args, **kwargs)

class ClassSchedule(models.Model):
    WEEKDAYS = [
        (0, _('Δευτέρα')),
        (1, _('Τρίτη')),
        (2, _('Τετάρτη')),
        (3, _('Πέμπτη')),
        (4, _('Παρασκευή')),
    ]

    TIME_SLOTS = [
        ('08:00-09:00', '08:00-09:00'),
        ('09:00-10:00', '09:00-10:00'),
        ('10:00-11:00', '10:00-11:00'),
        ('11:00-12:00', '11:00-12:00'),
        ('12:00-13:00', '12:00-13:00'),
        ('13:00-14:00', '13:00-14:00'),
        ('14:00-15:00', '14:00-15:00'),
        ('15:00-16:00', '15:00-16:00'),
        ('16:00-17:00', '16:00-17:00'),
        ('17:00-18:00', '17:00-18:00'),
    ]

    class_instance = models.ForeignKey(
        Class, 
        on_delete=models.CASCADE,
        related_name='schedule'
    )
    weekday = models.IntegerField(_('Ημέρα'), choices=WEEKDAYS)
    time_slot = models.CharField(_('Ώρα'), max_length=20, choices=TIME_SLOTS)
    activity = models.CharField(_('Δραστηριότητα'), max_length=100, blank=True)

    class Meta:
        verbose_name = _('Πρόγραμμα')
        verbose_name_plural = _('Προγράμματα')
        unique_together = ['class_instance', 'weekday', 'time_slot']
        ordering = ['weekday', 'time_slot']

    def __str__(self):
        return f"{self.class_instance.name} - {self.get_weekday_display()} {self.time_slot}"

class TeacherAssignment(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='class_assignments',
        verbose_name=_('Εκπαιδευτικός')
    )
    class_group = models.ForeignKey(
        'Class',  # Your existing Class model
        on_delete=models.CASCADE,
        related_name='teacher_assignments',
        verbose_name=_('Τμήμα')
    )
    is_active = models.BooleanField(_('Ενεργό'), default=True)
    assigned_date = models.DateField(_('Ημερομηνία Ανάθεσης'), auto_now_add=True)

    class Meta:
        verbose_name = _('Ανάθεση Εκπαιδευτικού')
        verbose_name_plural = _('Αναθέσεις Εκπαιδευτικών')
        unique_together = ['teacher', 'class_group']  # One teacher per class

    def __str__(self):
        return f"{self.teacher.get_full_name()} - {self.class_group.name}"
