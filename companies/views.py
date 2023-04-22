from django.shortcuts import render
from rest_framework import generics, viewsets, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from companies.models import Company, Qualification
from companies.serializers import CompanySerializer, WorkerSerializer, QualificationSerializer
from permission.permission import IsCompany, IsCompanyWorker
from workers.models import Worker


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
