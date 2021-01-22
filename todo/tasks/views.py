from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.contrib.auth.models import User
from django.shortcuts import render, HttpResponseRedirect
from django.views.generic import TemplateView, DetailView, CreateView, FormView, UpdateView, ListView, DeleteView
from django.views.generic.edit import ModelFormMixin
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.utils.http import url_has_allowed_host_and_scheme


from .models import Task, Project
from .forms import TaskForm, ProjectForm


def check_user_permission(user, object, type):
    onwer = getattr(object, 'owner', None) or getattr(object, 'author', None)
    object_project = getattr(object, 'project', object)
    if user == onwer or object_project in getattr(user, f"permission_to_{type}").all():
        return True
    return False        


class TaskList(LoginRequiredMixin, TemplateView):
    """Представление для домашней страницы."""

    template_name = 'tasks/home.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        task_type = self.request.GET.get('type', self.kwargs.get('type', 'all'))
        context.update({
            'tasks': Task.objects.get_tasks(
                self.request.user, 
                task_type,
                tag=self.kwargs.get('tag')
                )
        })
        return context


class TaskCreate(LoginRequiredMixin, CreateView):
    form_class = TaskForm
    template_name = 'tasks/add_task.html'
    success_url = '/todo/tasks/'
    parent_task = None

    def get(self, request, *args, **kwargs):
        self.parent_task = self.get_parent_task()
        if check_user_permission(self.request.user, self.parent_task, 'create'):
            pass
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
        instance_data = {}
        if self.request.GET.get('project'):
            instance_data.update({
                'project': Project.objects.get(id=self.request.GET.get('project')),
            })
        if self.parent_task:
            instance_data.update({
                'project': self.parent_task.project,
                'deadline_date': self.parent_task.deadline_date,
                'deadline_time': self.parent_task.deadline_time,
            })
            print(instance_data)
        kwargs.update({'initial': instance_data, 'user': self.request.user})
        return kwargs
    
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["parent_task"] = self.parent_task
        return context

    def form_valid(self, form):
        form.instance.parent_task = self.parent_task
        form.instance.author = self.request.user
        return super().form_valid(form)


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/task_detail.html'

    def get_object(self, *args, **kwargs):
        obj = super().get_object(*args, **kwargs)
        if check_user_permission(self.request.user, obj, 'reed'):
            return obj
        else:
            return self.handle_no_permission()


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/update_task.html'
    redirect_url = '/tasks/'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.POST.get('toggle_status'):
            new_status = self.request.POST.get('toggle_status')
            if dict(self.object.STATUS_CHOICES).get(new_status):
                self.object.status = new_status
                self.object.save()
            return HttpResponseRedirect(self.get_redirect_url())
        return super().post(request, *args, **kwargs)

    def get_object(self, *args, **kwargs):
        obj = super().get_object(*args, **kwargs)
        if check_user_permission(self.request.user, obj, 'update'):
            return obj
        else:
            return self.handle_no_permission()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

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


class TaskDelete(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/task_delete.html'
    success_url = reverse_lazy('task-list')

    def get_object(self):
        obj = super().get_object()
        if check_user_permission(self.request.user, obj, 'delete'):
            return obj
        return self.handle_no_permission()


class ProjectCreate(LoginRequiredMixin, CreateView):
    model = Project
    fields = ['title', 'color']
    template_name = 'tasks/add_project.html'
    success_url = '/todo/tasks/'

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ProjectDetail(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'tasks/project_detail.html'

    def get_object(self):
        obj = super().get_object()
        if check_user_permission(self.request.user, obj, 'reed'):
            return obj
        else:
            return self.handle_no_permission()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data()
        task_status = self.request.GET.get('status', self.kwargs.get('status', 'active'))
        context.update({
            'tasks': Task.objects.filter(
                project=context.get('project'),
                parent_task=None,
                status=task_status
            ).order_by('deadline_date')
        })
        return context


class ProjectUpdate(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'tasks/project_update.html'
    form_class = ProjectForm

    def get_object(self):
        obj = super().get_object()
        if check_user_permission(self.request.user, obj, 'update'):
            return obj
        return self.handle_no_permission()

    def form_valid(self, form):  
        self.object = form.save()
        if self.request.POST.get('delete_user'):
            user_for_delete = User.objects.filter(id__in=self.request.POST.getlist('delete_user'))
            for permission in ['permission_to_reed', 'permission_to_create', 'permission_to_update', 'permission_to_delete']:
                getattr(self.object, permission).remove(*user_for_delete) 
            self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class ProjectAddUser(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'tasks/project_add_user.html'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if request.POST.get('user_email'):
            print(request.POST)
            try:
                new_user = User.objects.get(email=request.POST.get('user_email'))
            except User.DoesNotExist:
                print('пользователь не найден')
            else:
                self.object.permission_to_reed.add(new_user)
                self.object.save()
            return HttpResponseRedirect(self.get_success_url())
        
    def get_success_url(self):
        try:
            url = self.object.get_update_url()
        except AttributeError:
            url = super().get_success_url()
        return url

    def get_object(self):
        obj = super().get_object()
        if check_user_permission(self.request.user, obj, 'update'):
            return obj
        return self.handle_no_permission()

class ProjectDelete(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'tasks/project_delete.html'
    success_url = reverse_lazy('task-list')

    def get_object(self):
        obj = super().get_object()
        if check_user_permission(self.request.user, obj, 'delete'):
            return obj
        return self.handle_no_permission()