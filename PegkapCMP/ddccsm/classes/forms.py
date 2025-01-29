from django import forms
from .models import Class, ClassSchedule, Activity
from django.utils.translation import gettext_lazy as _
from .models import TeacherAssignment

class ClassForm(forms.ModelForm):
    activities = forms.ModelMultipleChoiceField(
        queryset=Activity.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False,
        label=_('Δραστηριότητες')
    )

    class Meta:
        model = Class
        fields = ['name', 'description', 'is_active', 'activities', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:  # If this is an edit form
            self.initial['activities'] = self.instance.activities.all()
            # If this is an existing class, populate schedule data
            if self.instance.pk:
                try:
                    schedule_entries = self.instance.schedule.all()
                    print("Found schedule entries:", schedule_entries)  # Debug print
                    
                    for entry in schedule_entries:
                        key = f'schedule-{entry.weekday}-{entry.time_slot}'
                        self.initial[key] = entry.activity
                        print(f"Setting initial data: {key} = {entry.activity}")  # Debug print
                    
                    print("Final initial data:", self.initial)  # Debug print
                except AttributeError:
                    pass

    def clean(self):
        cleaned_data = super().clean()
        # Collect all schedule fields
        self.schedule_data = {}
        for key, value in self.data.items():
            if key.startswith('schedule-') and value:
                # Extract weekday and time_slot from the key
                _, weekday, time_slot = key.split('-', 2)
                self.schedule_data[(int(weekday), time_slot)] = value
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            
            # Clear existing schedule entries
            instance.schedule.all().delete()
            
            # Create new schedule entries
            for (weekday, time_slot), activity in self.schedule_data.items():
                ClassSchedule.objects.create(
                    class_instance=instance,
                    weekday=weekday,
                    time_slot=time_slot,
                    activity=activity
                )
        return instance

class ClassScheduleFormSet(forms.ModelForm):
    class Meta:
        model = ClassSchedule
        fields = ['weekday', 'time_slot']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['weekday'].widget = forms.CheckboxSelectMultiple(
            choices=ClassSchedule.WEEKDAYS
        )
        self.fields['time_slot'].widget = forms.CheckboxSelectMultiple(
            choices=ClassSchedule.TIME_SLOTS
        )

class TeacherAssignmentForm(forms.ModelForm):
    class Meta:
        model = TeacherAssignment
        fields = ['teacher', 'class_group', 'is_active']
        widgets = {
            'teacher': forms.Select(attrs={'class': 'form-control'}),
            'class_group': forms.Select(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        } 