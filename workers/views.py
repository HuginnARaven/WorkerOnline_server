from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet


from workers.models import TaskAppointment, WorkerLogs, WorkerTaskComment
from workers.permission import IsWorker
from workers.serializers import TaskDoneSerializer, WorkersLogSerializer, WorkerTaskCommentSerializer


class TaskDoneView(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = TaskAppointment.objects.all()
    serializer_class = TaskDoneSerializer
    permission_classes = [IsAuthenticated, IsWorker, ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_done', ]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(worker_appointed=self.request.user.id, )


class WorkersLogView(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = WorkerLogs.objects.all()
    serializer_class = WorkersLogSerializer
    permission_classes = [IsAuthenticated, IsWorker, ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['datetime__date', 'type']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(worker=self.request.user.id, )


class WorkerTaskCommentView(viewsets.ModelViewSet):
    queryset = WorkerTaskComment.objects.all()
    serializer_class = WorkerTaskCommentSerializer
    permission_classes = [IsAuthenticated, IsWorker, ]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(task_appointment__worker_appointed=self.request.user.id)
