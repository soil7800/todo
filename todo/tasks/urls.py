from django.urls import path

from .views import Todo, TaskDetail, AddTask, AddTag, UpdateTask


urlpatterns = [
    path('<str:type>/', Todo.as_view(), name='todo-list-by-type'),
    path('tag/<slug:tag>/', Todo.as_view(), name='todo-list-by-tag', kwargs={'type': 'all'}),
    path('task/<int:pk>/', TaskDetail.as_view(), name='task-detail'),
    path('task/<int:pk>/new_subtask/', AddTask.as_view(), name='add-subtask'),
    path('todo/new_task/', AddTask.as_view(), name='add-task'),
    path('todo/new_tag/', AddTag.as_view(), name='add-tag'),
    path('task/<int:pk>/update/', UpdateTask.as_view(), name='update-task'),
]