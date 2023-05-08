from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
import django_filters.rest_framework
from rest_framework import generics, viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from companies.models import Company, Qualification, Task
from companies.serializers import CompanySerializer, WorkerSerializer, QualificationSerializer, TaskSerializer, \
    TaskAppointmentSerializer, WorkerLogSerializer, WorkerTaskCommentSerializer
from permission.permission import IsCompany, IsCompanyWorker
from workers.models import Worker, TaskAppointment, WorkerLogs, WorkerTaskComment


class CompanySinUpView(mixins.CreateModelMixin, GenericViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class WorkerView(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer
    permission_classes = [IsAuthenticated, IsCompanyWorker, ]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(employer=self.request.user.id)


class QualificationView(viewsets.ModelViewSet):
    queryset = Qualification.objects.all()
    serializer_class = QualificationSerializer
    permission_classes = [IsAuthenticated, IsCompany, ]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(company=self.request.user.id)


class TaskView(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, IsCompany, ]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(company=self.request.user.id)


class TaskAppointmentView(mixins.CreateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = TaskAppointment.objects.all()
    serializer_class = TaskAppointmentSerializer
    permission_classes = [IsAuthenticated, IsCompany, ]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(task_appointed__company=self.request.user.id, )


class WorkerLogView(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = WorkerLogs.objects.all()
    serializer_class = WorkerLogSerializer
    permission_classes = [IsAuthenticated, IsCompany, ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['worker', 'datetime__date', 'type']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(task__company=self.request.user.id)


class WorkerTaskCommentView(viewsets.ModelViewSet):
    queryset = WorkerTaskComment.objects.all()
    serializer_class = WorkerTaskCommentSerializer
    permission_classes = [IsAuthenticated, IsCompany, ]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(task_appointment__worker_appointed__employer=self.request.user.id)
