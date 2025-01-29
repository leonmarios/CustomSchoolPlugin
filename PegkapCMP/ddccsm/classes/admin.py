from django.contrib import admin
from .models import Class, ClassSchedule

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_filter = ['is_active']

@admin.register(ClassSchedule)
class ClassScheduleAdmin(admin.ModelAdmin):
    list_display = ['class_instance', 'weekday', 'time_slot']
    list_filter = ['weekday', 'time_slot']
