from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from companies.views import CompanySinUpView, WorkerView, QualificationView, TaskView, TaskAppointmentView, \
    WorkerLogView, WorkerTaskCommentView

company_router = routers.SimpleRouter()
company_router.register(r'singup', CompanySinUpView, basename='singup')
company_router.register(r'worker', WorkerView, basename='worker')
company_router.register(r'logs', WorkerLogView, basename='logs')
company_router.register(r'qualification', QualificationView, basename='qualification')
company_router.register(r'task', TaskView, basename='task')
company_router.register(r'appointment', TaskAppointmentView, basename='appointment')
company_router.register(r'comment-task', WorkerTaskCommentView, basename='comment-task')

urlpatterns = [
    path('company/', include(company_router.urls)),
]
