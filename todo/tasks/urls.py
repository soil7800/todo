from django.urls import path

from .views import TaskList, TaskCreate, TaskDetail, TaskUpdate, TaskDelete,  ProjectCreate, ProjectDetail, ProjectUpdate, ProjectDelete, ProjectAddUser


urlpatterns = [
    path('tasks/', TaskList.as_view(), name='task-list'),
    path('tasks/new_task/', TaskCreate.as_view(), name='task-create'),
    path('tasks/<int:pk>/', TaskDetail.as_view(), name='task-detail'),
    path('tasks/<int:pk>/new_subtask/', TaskCreate.as_view(), name='task-create-subtask'),
    path('tasks/<int:pk>/update/', TaskUpdate.as_view(), name='task-update'),
    path('tasks/<int:pk>/delete/', TaskDelete.as_view(), name='task-delete'),
    path('project/new_project/', ProjectCreate.as_view(), name='project-create'),
    path('project/<int:pk>/', ProjectDetail.as_view(), name='project-detail'),
    path('project/<int:pk>/update/', ProjectUpdate.as_view(), name='project-update'),
    path('project/<int:pk>/delete/', ProjectDelete.as_view(), name='project-delete'),
    path('project/<int:pk>/add-user/', ProjectAddUser.as_view(), name='project-add-user'),
]