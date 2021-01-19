from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Task, Tag


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            'title', 
            'deadline_date', 
            'deadline_time', 
            'tag', 
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            if self.initial.get('author'):
                author = self.initial.get('author')
            else:
                author = self.instance.author
        except Task.author.RelatedObjectDoesNotExist:
            return
        else:
            self.fields['tag'].queryset = Tag.objects.filter(author=author)   
    
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
        print('очищеные данные - ', self.cleaned_data.get('deadline_date'), self.cleaned_data.get('deadline_time'))
        date = self.cleaned_data.get('deadline_date')
        time = self.cleaned_data.get('deadline_time')
        parrent_task = self.instance.parent_task
        if parrent_task and parrent_task.deadline_time:
            if time > parent_deadline_time:
                raise ValidationError('Время подзадачи не может быть позже чем у основной задачи')
        if date == timezone.localdate() and time != None and time < timezone.localtime().time():
            raise ValidationError('Нельзя выбрать прошедшее время')
        return time

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['title', 'color']