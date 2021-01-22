from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Task, Project


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title', 
            'deadline_date', 
            'deadline_time', 
            'project', 
        ]

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            author = self.instance.author
        except Task.author.RelatedObjectDoesNotExist:
            author = None
        if author and author != user:
            self.fields['project'].queryset = self.instance.project
        else:
            self.fields['project'].queryset = Project.objects.filter(owner=user)
    
    def clean_deadline_date(self):
        data = self.cleaned_data['deadline_date']
        parrent_task = self.instance.parent_task
        if parrent_task:
            parent_deadline_date = parrent_task.deadline_date
            if data > parent_deadline_date:
                raise ValidationError('Дата подзадачи не может быть позже чем у основной задачи')
        if data < timezone.localdate():
            raise ValidationError('Нельзя выбрать прошедшую дату')
        return data
    
    def clean_deadline_time(self):
        date = self.cleaned_data.get('deadline_date')
        time = self.cleaned_data.get('deadline_time')
        parrent_task = self.instance.parent_task
        if parrent_task and parrent_task.deadline_time:
            if time > parent_deadline_time:
                raise ValidationError('Время подзадачи не может быть позже чем у основной задачи')
        if date == timezone.localdate() and time != None and time < timezone.localtime().time():
            raise ValidationError('Нельзя выбрать прошедшее время')
        return time


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            'title',
            'color',
            'permission_to_reed',
            'permission_to_create',
            'permission_to_update',
            'permission_to_delete',
        ]

class ProjectAddUser(forms.ModelForm):
    pass