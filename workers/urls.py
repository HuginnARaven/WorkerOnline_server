from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from workers.views import TaskDoneView, WorkersLogView, WorkerTaskCommentView, VoteView, GetVoting, GetTasksCommentView

worker_router = routers.SimpleRouter()
worker_router.register(r'tasks', TaskDoneView, basename='tasks')
worker_router.register(r'logs', WorkersLogView, basename='logs')
worker_router.register(r'comment-task', WorkerTaskCommentView, basename='comment-task')
worker_router.register(r'vote', VoteView, basename='vote')
worker_router.register(r'voting', GetVoting, basename='voting')

urlpatterns = [
    path('worker/', include(worker_router.urls)),
    path('worker/task/<int:task_pk>/comments/', GetTasksCommentView.as_view())
]
