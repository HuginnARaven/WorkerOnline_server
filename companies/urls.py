from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from companies.views import CompanySinUpView, WorkerView, QualificationView

company_router = routers.SimpleRouter()
company_router.register(r'singup', CompanySinUpView, basename='singup')
company_router.register(r'worker', WorkerView, basename='worker')
company_router.register(r'qualification', QualificationView, basename='qualification')

urlpatterns = [
    path('company/', include(company_router.urls)),
]
