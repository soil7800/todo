from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView, DetailView, CreateView, FormView
from django.utils import timezone

from .models import Task, Tag
from .forms import TaskForm, TagForm


class Todo(LoginRequiredMixin, TemplateView):
    """Представление для домашней страницы."""
    login_url = '/login/'
    template_name = 'tasks/home.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data()
        task = Task.objects.get(id=self.request.POST.get("id"))
        if task.status != "completed":
            task.status = "completed"
        else:
            task.status = "active"
        task.save()
        return super().render_to_response(context)

    def get_context_data(self, *args, **kwargs):
        context = {
            'tasks': Task.objects.get_tasks(
                self.request.user, 
                self.kwargs.get('type'),
                tag=self.kwargs.get('tag')
                )
        }
        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    




class AddTask(LoginRequiredMixin, FormView):
    form_class = TaskForm
    template_name = 'tasks/add_task.html'
    success_url = '/todo/all/'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class AddTag(LoginRequiredMixin, CreateView):
    model = Tag
    fields = ['title', 'color']
    template_name = 'tasks/add_tag.html'
    success_url = '/todo/all/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)