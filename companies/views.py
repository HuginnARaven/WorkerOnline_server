from django.shortcuts import render
from django_filters import DateFromToRangeFilter, DateTimeFromToRangeFilter, DateTimeFilter, IsoDateTimeFilter, \
    DateFilter
from django_filters.rest_framework import DjangoFilterBackend, FilterSet

from rest_framework import generics, viewsets, status, mixins, filters
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

from companies.models import Company, Qualification, Task, TaskVoting
from companies.serializers import CompanySerializer, WorkerSerializer, QualificationSerializer, TaskSerializer, \
    TaskAppointmentSerializer, WorkerLogSerializer, TaskRecommendationSerializer, \
    WorkerReportSerializer, AutoAppointmentSerializer, CompanyTaskCommentSerializer, WorkerScheduleSerializer, \
    VotingSerializer, VotingResultSerializer
from companies.permission import IsCompany, IsCompanyWorker, IsCompanyOwner
from workers.models import Worker, TaskAppointment, WorkerLogs, WorkerTaskComment, WorkerSchedule


class CustomStandartPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


class CompanySinUpView(mixins.CreateModelMixin, GenericViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class WorkerView(viewsets.ModelViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerSerializer
    permission_classes = [IsAuthenticated, IsCompanyWorker, ]
    filter_backends = [filters.SearchFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(employer=self.request.user.id)


class WorkerScheduleView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin,  GenericViewSet):
    queryset = WorkerSchedule.objects.all()
    serializer_class = WorkerScheduleSerializer
    permission_classes = [IsAuthenticated, IsCompanyOwner]


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
    # pagination_class = CustomStandartPagination

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


class LogFilter(FilterSet):
    datetime = DateTimeFromToRangeFilter()
    date = DateFilter(field_name='datetime', lookup_expr='date')

    class Meta:
        model = WorkerLogs
        fields = ['worker', 'type', 'datetime', 'date']


class WorkerLogView(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = WorkerLogs.objects.all()
    serializer_class = WorkerLogSerializer
    permission_classes = [IsAuthenticated, IsCompany, ]
    filter_backends = [DjangoFilterBackend]
    filterset_class = LogFilter
    pagination_class = CustomStandartPagination

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(task__company=self.request.user.id)


class CompanyTaskCommentView(viewsets.ModelViewSet):
    queryset = WorkerTaskComment.objects.all()
    serializer_class = CompanyTaskCommentSerializer
    permission_classes = [IsAuthenticated, IsCompany, ]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(task_appointment__worker_appointed__employer=self.request.user.id)


class TaskRecommendationView(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskRecommendationSerializer
    permission_classes = [IsAuthenticated, IsCompany, ]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(company=self.request.user.id, task_appointment=None)


class WorkerReportView(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = Worker.objects.all()
    serializer_class = WorkerReportSerializer
    permission_classes = [IsAuthenticated, IsCompany, ]

    @method_decorator(cache_page(60 * 2))
    @method_decorator(vary_on_headers("Authorization", ))
    def list(self, *args, **kwargs):
        return super().list(*args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(employer=self.request.user.id)


class AutoAppointmentView(generics.RetrieveAPIView):
    queryset = Company.objects.all()
    serializer_class = AutoAppointmentSerializer
    permission_classes = [IsAuthenticated, IsCompany, ]

    def get_object(self):
        qs = super().get_queryset()
        return get_object_or_404(qs, id=self.request.user.id)


class VotingView(viewsets.ModelViewSet):
    queryset = TaskVoting.objects.all()
    serializer_class = VotingSerializer
    permission_classes = [IsAuthenticated, IsCompany, ]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(company=self.request.user.company)


class GetVotingResult(mixins.RetrieveModelMixin, mixins.ListModelMixin, GenericViewSet):
    queryset = TaskVoting.objects.all()
    serializer_class = VotingResultSerializer
    permission_classes = [IsAuthenticated, IsCompany, ]

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(company=self.request.user.company)
