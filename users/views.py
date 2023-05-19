from django.shortcuts import render
from rest_framework import generics, viewsets, status, mixins
from rest_framework import status
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.utils.translation import gettext_lazy as _

from companies.models import Company
from users.models import UserAccount
from users.serializers import UserAccountSerializer, CompanyProfileSerializer, WorkerProfileSerializer, \
    ChangePasswordSerializer
from workers.models import Worker


class LogInView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'role': user.role
        })


class LogOutView(APIView):
    def post(self, request, format=None):
        request.auth.delete()
        return Response(status=status.HTTP_200_OK)


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
