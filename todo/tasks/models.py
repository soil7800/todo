from django.db import models
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
        if kwargs.get('tag'):
            queryset = queryset.filter(tag__slug=kwargs['tag'])
        return queryset
    
    def _get_overdue_tasks(self, user, **kwargs):
        queryset = self.filter(
            author=user,
            deadline_date__lt=timezone.now().date(), 
            status='active',
            parent_task=None
        )
        if kwargs.get('tag'):
            queryset = queryset.filter(tag__slug=kwargs['tag'])
        return queryset
    
    def _get_coming_tasks(self, user, **kwargs):
        queryset = self.filter(
            author=user, 
            deadline_date__gt=timezone.now().date(),
            status='active',
            parent_task=None
        )
        if kwargs.get('tag'):
            queryset = queryset.filter(tag__slug=kwargs['tag'])
        return queryset
    
    def _get_completed_tasks(self, user, **kwargs):
        queryset = self.filter(
            author=user,
            status='completed',
            parent_task=None
        )
        if kwargs.get('tag'):
            queryset = queryset.filter(tag__slug=kwargs['tag'])
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
        tasks = {'overdue': self._get_overdue_tasks(user, tag=kwargs.get('tag'))}
        if task_type == 'today' or task_type == 'all':
            tasks['today'] = self._get_today_tasks(user, tag=kwargs.get('tag'))
        if task_type == 'coming' or task_type == 'all':
            tasks['coming'] = self._get_coming_tasks(user, tag=kwargs.get('tag'))
        if task_type == 'all':
            tasks['completed'] = self._get_completed_tasks(user, tag=kwargs.get('tag'))
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
    tag = models.ForeignKey(
        to='Tag', 
        on_delete=models.CASCADE, 
        verbose_name='Тег', 
        null=True,
        blank=True,
    )

    def is_current_year(self):
        return self.deadline_date.year == timezone.localdate().year

    def __str__(self):
        return self.title

    def _check_updated_fields(self):
        field_check_list = ('tag', 'status')
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
        return reverse('task-detail', args=[self.id])

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'


class Tag(models.Model):
    """Тэг для задач."""

    title = models.CharField('Заголовок', max_length=255)
    _original_title = None
    slug = models.SlugField(max_length=255, blank=True)
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name='Автор'
    )
    color = models.CharField(
        'Цвет', 
        max_length=100, 
        blank=True, 
        default=None,
    )

    def __str__(self):
        return self.title

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_title = self.title

    def save(self, *args, **kwargs):
        if not self.id or self.title != self._original_title:
            self.slug = generate_slug_from_russian(self.title)
        super().save(*args, **kwargs)
        self._original_title = self.title

    def get_text_color(self):
        if self.color and int(self.color[1:], 16) < 0x999999:
            return '#fff'
        return '#000'

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        constraints = [
            models.UniqueConstraint(fields=['author', 'title'], name='unique-title')
        ]
    

