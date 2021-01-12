from django.contrib import admin

from .models import Task, Tag
from .forms import TaskForm


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'created', 'deadline_date', 'status')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('author', 'title')