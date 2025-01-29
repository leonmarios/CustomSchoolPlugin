from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import FormField, Learner, SocialHistory

@admin.register(FormField)
class FormFieldAdmin(admin.ModelAdmin):
    list_display = ['name', 'label', 'field_type', 'section', 'required', 'is_active', 'order']
    list_filter = ['section', 'field_type', 'required', 'is_active']
    search_fields = ['name', 'label']
    ordering = ['section', 'order']
    
    fieldsets = (
        (_('Βασικές Πληροφορίες'), {
            'fields': (
                'name',
                'label',
                'field_type',
                'section',
            )
        }),
        (_('Ρυθμίσεις'), {
            'fields': (
                'required',
                'is_active',
                'order',
                'help_text',
            )
        }),
        (_('Επιλογές'), {
            'fields': ('choices',),
            'classes': ('collapse',),
            'description': _('Συμπληρώστε τις επιλογές μόνο για πεδία τύπου "select". Μία επιλογή ανά γραμμή.')
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['name'].help_text = _('Το όνομα του πεδίου στη βάση δεδομένων (μόνο λατινικοί χαρακτήρες, χωρίς κενά)')
        return form

class SocialHistoryInline(admin.StackedInline):
    model = SocialHistory
    extra = 1

@admin.register(Learner)
class LearnerAdmin(admin.ModelAdmin):
    inlines = [SocialHistoryInline]
    list_display = ['first_name', 'last_name', 'status']
    search_fields = ['first_name', 'last_name']
    list_filter = ['status']

@admin.register(SocialHistory)
class SocialHistoryAdmin(admin.ModelAdmin):
    list_display = ['learner', 'status', 'arrival_date']
    list_filter = ['status', 'arrival_date']
    search_fields = ['learner__first_name', 'learner__last_name', 'comments']
    date_hierarchy = 'arrival_date'
