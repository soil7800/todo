from django.contrib import admin

from .models import Task, Project, UserProfile
from .forms import TaskForm


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'created', 'deadline_date', 'status')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    fields = [
        'title', 
        'owner', 
        'color', 
        'permission_to_create', 
        'permission_to_reed', 
        'permission_to_update', 
        'permission_to_delete',
    ]

@admin.register(UserProfile)
class ProjectAdmin(admin.ModelAdmin):
    fields = [
        'user'
    ]