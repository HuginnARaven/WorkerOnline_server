from rest_framework import generics, viewsets, status, mixins
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from rest_framework.viewsets import GenericViewSet
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie, vary_on_headers

from companies.models import Company
from users.models import UserAccount, TechSupportRequest
from users.serializers import UserAccountSerializer, CompanyProfileSerializer, WorkerProfileSerializer, \
    ChangePasswordSerializer, TechSupportRequestSerializer
from workers.models import Worker


class ChangePasswordView(generics.UpdateAPIView):
    queryset = UserAccount.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(id=self.request.user.id)

    def get_object(self):
        try:
            return UserAccount.objects.get(pk=self.request.user.id)
        except UserAccount.DoesNotExist:
            raise UserAccount()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        result = {
            "password": _("Password has been changed successfully"),
        }
        return Response(result)


class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.role == 'C':
            return Company
        if self.request.user.role == 'W':
            return Worker

    def get_serializer_class(self):
        if self.request.user.role == 'C':
            return CompanyProfileSerializer
        if self.request.user.role == 'W':
            return WorkerProfileSerializer

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.request.user.id)
        return obj


class TechSupportRequestView(viewsets.ModelViewSet, GenericViewSet):
    queryset = TechSupportRequest.objects.all()
    serializer_class = TechSupportRequestSerializer
    permission_classes = [IsAuthenticated, ]

    # @method_decorator(cache_page(60 * 5))
    # @method_decorator(vary_on_headers("Authorization", ))
    # def list(self, *args, **kwargs):
    #     return super().list(*args, **kwargs)

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(user=self.request.user)

