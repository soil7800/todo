from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import TemplateView, DetailView, CreateView, FormView, UpdateView
from django.views.generic.edit import ModelFormMixin
from django.utils import timezone
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Task, Tag
from .forms import TaskForm, TagForm


class Todo(LoginRequiredMixin, TemplateView):
    """Представление для домашней страницы."""

    template_name = 'tasks/home.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        context.update({
            'tasks': Task.objects.get_tasks(
                self.request.user, 
                self.kwargs.get('type'),
                tag=self.kwargs.get('tag')
                )
        })
        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'

    def check_object_permission(self):
        pass


class AddTask(LoginRequiredMixin, CreateView):
    form_class = TaskForm
    template_name = 'tasks/add_task.html'
    success_url = '/todo/all/'
    parent_task = None

    def get(self, request, *args, **kwargs):
        self.parent_task = self.get_parent_task()
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.parent_task = self.get_parent_task()
        return super().post(request, *args, **kwargs)

    def get_parent_task(self):
        if self.kwargs.get('pk'):
            parent_task = Task.objects.get(id=self.kwargs['pk'])
            return parent_task

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        instance_data = {'author': self.request.user}
        if self.request.GET.get('tag'):
            instance_data.update({
                'tag': Tag.objects.get(slug=self.request.GET.get('tag')),
            })
        if self.parent_task:
            instance_data.update({
                'tag': self.parent_task.tag, 
                'deadline_date': self.parent_task.deadline_date,
                'deadline_time': self.parent_task.deadline_time,
                'parent_task': self.parent_task})
        kwargs.update({'initial': instance_data})
        return kwargs
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["parent_task"] = self.parent_task
        return context

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


class UpdateTask(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/update_task.html'
    redirect_url = '/todo/all/'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.POST.get('toggle_status'):
            new_status = self.request.POST.get('toggle_status')
            if dict(self.object.STATUS_CHOICES).get(new_status):
                self.object.status = new_status
                self.object.save()
            return HttpResponseRedirect(self.get_redirect_url())
        return super().post(request, *args, **kwargs)

    def get_success_url(self):
        url = self.get_redirect_url()
        if self.redirect_url != url:
            return url
        else:
            return super().get_success_url()

    def get_redirect_url(self):
        redirect_to = self.request.POST.get(
            'next',
            self.request.GET.get('next', '')
        )
        url_is_safe = url_has_allowed_host_and_scheme(
            url=redirect_to,
            allowed_hosts=self.request.get_host(),
            require_https=self.request.is_secure(),
        )
        return redirect_to if url_is_safe else self.redirect_url

