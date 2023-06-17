from django.shortcuts import render
from django_filters import DateTimeFromToRangeFilter, DateFilter
from rest_framework import generics, viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from django_filters.rest_framework import DjangoFilterBackend, FilterSet

from companies.models import TaskVoting
from companies.views import LogFilter, CustomStandartPagination
from workers.models import TaskAppointment, WorkerLogs, WorkerTaskComment, TaskVote
from workers.permission import IsWorker
from workers.serializers import TaskDoneSerializer, WorkersLogSerializer, WorkerTaskCommentSerializer, VoteSerializer, \
    GetVotingSerializer


class TaskDoneView(mixins.UpdateModelMixin, mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = TaskAppointment.objects.all()
    serializer_class = TaskDoneSerializer
    permission_classes = [IsAuthenticated, IsWorker, ]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_done', ]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(worker_appointed=self.request.user.id, )


class WorkerLogFilter(FilterSet):
    datetime = DateTimeFromToRangeFilter()
    date = DateFilter(field_name='datetime', lookup_expr='date')

    class Meta:
        model = WorkerLogs
        fields = ['type', 'datetime', 'date']


class WorkersLogView(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = WorkerLogs.objects.all()
    serializer_class = WorkersLogSerializer
    permission_classes = [IsAuthenticated, IsWorker, ]
    filter_backends = [DjangoFilterBackend]
    filterset_class = WorkerLogFilter

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


class GetTasksCommentView(generics.ListAPIView):
    queryset = WorkerTaskComment.objects.all()
    serializer_class = WorkerTaskCommentSerializer
    permission_classes = [IsAuthenticated, IsWorker, ]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(task_appointment__id=self.kwargs['task_pk'], task_appointment__worker_appointed=self.request.user.id)


class VoteView(viewsets.ModelViewSet):
    queryset = TaskVote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated, IsWorker, ]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(worker=self.request.user.worker)


class GetVoting(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = TaskVoting.objects.all()
    serializer_class = GetVotingSerializer
    permission_classes = [IsAuthenticated, IsWorker, ]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(company=self.request.user.worker.employer)
