from django import forms

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

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['tag'].queryset = Tag.objects.filter(author=user)

class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['title', 'color']