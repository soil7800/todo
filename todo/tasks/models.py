from django.db import models
from django.db.models.signals import post_save
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse


from .utils import generate_slug_from_russian


class TaskManager(models.Manager):
    def _get_today_tasks(self, user, **kwargs):
        queryset = self.filter(
            author=user, 
            deadline_date=timezone.now().date(),
            status='active',
            parent_task=None
        )
        if kwargs.get('project'):
            queryset = queryset.filter(project__id=kwargs['project'])
        return queryset
    
    def _get_overdue_tasks(self, user, **kwargs):
        queryset = self.filter(
            author=user,
            deadline_date__lt=timezone.now().date(), 
            status='active',
            parent_task=None
        )
        if kwargs.get('project'):
            queryset = queryset.filter(project__id=kwargs['project'])
        return queryset
    
    def _get_coming_tasks(self, user, **kwargs):
        queryset = self.filter(
            author=user, 
            deadline_date__gt=timezone.now().date(),
            status='active',
            parent_task=None
        )
        if kwargs.get('project'):
            queryset = queryset.filter(project__id=kwargs['project'])
        return queryset
    
    def _get_completed_tasks(self, user, **kwargs):
        queryset = self.filter(
            author=user,
            status='completed',
            parent_task=None
        )
        if kwargs.get('project'):
            queryset = queryset.filter(project__id=kwargs['project'])
        return queryset
    
    def _get_archived_tasks(self, user):
        queryset = self.filter(
            author=user,
            status='archived',
            parent_task=None
        )
        return queryset

    def get_tasks(self, user, task_type, **kwargs):
        if task_type == 'archived':
            return {'archived': self._get_archived_tasks(user)}
        tasks = {'overdue': self._get_overdue_tasks(user, project=kwargs.get('project_id'))}
        if task_type == 'today' or task_type == 'all':
            tasks['today'] = self._get_today_tasks(user, project=kwargs.get('project_id'))
        if task_type == 'coming' or task_type == 'all':
            tasks['coming'] = self._get_coming_tasks(user, project=kwargs.get('project_id'))
        if task_type == 'all':
            tasks['completed'] = self._get_completed_tasks(user, project=kwargs.get('project_id'))
        return tasks


class Task(models.Model):
    """Задача пользователя."""
    objects = TaskManager()
    STATUS_CHOICES = [
        ('active', 'активная'),
        ('completed', 'выполненная'),
        ('archived', 'архивированная'),
    ]
    title = models.CharField('Заголовок', max_length=255)
    created = models.DateTimeField('Дата создания', auto_now_add=True)
    updated = models.DateTimeField('Дата последнего изменения', auto_now=True)
    deadline_date = models.DateField('Дата', default=timezone.now)
    deadline_time = models.TimeField('Время', blank=True, null=True)
    status = models.CharField(
        'Статус',
        max_length=100,  
        choices=STATUS_CHOICES, 
        default='active'
    )
    parent_task = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        verbose_name='Родительская задача', 
        null=True, 
        blank=True
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='Автор'
    )
    project = models.ForeignKey(
        to='Project', 
        on_delete=models.CASCADE, 
        verbose_name='Проект', 
        null=True,
        blank=True,
    )

    def is_current_year(self):
        return self.deadline_date.year == timezone.localdate().year

    def is_overdue(self):
        if self.deadline_date == timezone.localdate():
            if not self.deadline_time or self.deadline_time > timezone.localtime().time():
                return False
            return True
        elif self.deadline_date < timezone.localdate():
            return True
        else:
            return False
        

    def __str__(self):
        return self.title

    def _check_updated_fields(self):
        field_check_list = ('project', 'status')
        updated_fields = []
        origin_instance = Task.objects.get(id=self.id)
        for field in field_check_list:
            if getattr(origin_instance, field) != getattr(self, field):
                updated_fields.append(field)
        return updated_fields or None

    def _update_child_task(self, fields):
        if fields:
            for task in self.task_set.all():
                for field in fields:
                    setattr(task, field, getattr(self, field))
                    task.save()

    def save(self, *args, **kwargs):
        if self.id and self.task_set.all():
            updated_fields = self._check_updated_fields()
            self._update_child_task(updated_fields)
        super().save(*args, **kwargs)

    def get_child_task_status(self):
        if self.task_set.count() != 0:
            return {
                'completed': self.task_set.filter(status='completed').count(),
                'all': self.task_set.count()
            }
        return None

    def get_absolute_url(self):
        return reverse('task-detail', kwargs={'pk': self.id})
    
    def get_update_url(self):
        return reverse('task-update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('task-delete', kwargs={'pk': self.id})

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'


class Project(models.Model):
    """"""

    title = models.CharField('Заголовок', max_length=255)
    color = models.CharField(
        'Цвет', 
        max_length=100, 
        blank=True, 
        default=None,
    )
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='Владелец'
    )
    permission_to_create = models.ManyToManyField(
        User, 
        related_name='permission_to_create',
        blank=True
    )
    permission_to_reed = models.ManyToManyField(
        User, 
        related_name='permission_to_reed',
        blank=True
    )
    permission_to_update = models.ManyToManyField(
        User, 
        related_name='permission_to_update',
        blank=True
    )
    permission_to_delete = models.ManyToManyField(
        User, 
        related_name='permission_to_delete',
        blank=True
    )

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        constraints = [
            models.UniqueConstraint(fields=['owner', 'title'], name='unique-title')
        ]
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('project-detail', kwargs={'pk': self.id})
    
    def get_update_url(self):
        return reverse('project-update', kwargs={'pk': self.id})

    def get_delete_url(self):
        return reverse('project-delete', kwargs={'pk': self.id})
    
    def get_add_user_url(self):
        return reverse('project-add-user', kwargs={'pk': self.id})


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        return str(self.user)

    def get_projects(self):
        user_projects = self.user.project_set.all()
        available_projects = self.user.permission_to_reed.all().exclude(owner=self.user)
        all_projects = user_projects.union(available_projects)
        return all_projects


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
