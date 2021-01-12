from django.urls import path

from .views import Todo, TaskDetail, AddTask, AddTag


urlpatterns = [
    path('<str:type>/', Todo.as_view(), name='todo-list-by-type'),
    path('tag/<slug:tag>/', Todo.as_view(), name='todo-list-by-tag', kwargs={'type': 'all'}),
    path('task/<int:pk>/', TaskDetail.as_view(), name='task-detail'),
    path('todo/new_task/', AddTask.as_view(), name='add-task'),
    path('todo/new_tag/', AddTag.as_view(), name='add-tag'),
]