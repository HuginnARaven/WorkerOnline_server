import datetime

import pytz
from rest_framework import serializers
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _

from iot.models import Supervisor
from workers.models import Worker, WorkerLogs, TaskAppointment


class SupervisorOptionsSerializer(serializers.ModelSerializer):
    day_start = serializers.TimeField(source="worker.day_start")
    day_end = serializers.TimeField(source="worker.day_end")
    timezone = serializers.CharField(source="company.timezone")

    class Meta:
        model = Supervisor
        fields = [
            "worker",
            "day_start",
            "day_end",
            "timezone",
            "in_admin_mode",
        ]


class SupervisorCompanySerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(read_only=True)
    last_active = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Supervisor
        fields = [
            "in_admin_mode",
            "worker",
            "is_active",
            "last_active",
        ]

    def validate(self, data):
        if data.get('worker'):
            if not Worker.objects.filter(id=data['worker'].id,
                                         employer=self.context['request'].user.company):
                raise serializers.ValidationError({'detail': [
                    _('The assigned worker does not exist or belong to your company!')
                ]})
            if Supervisor.objects.filter(worker=data['worker']):
                raise serializers.ValidationError({'detail': [
                    _('The assigned worker already have Supervisor!')
                ]})

        return data

    def create(self, validated_data):
        return Supervisor.objects.create(
            in_admin_mode=validated_data['in_admin_mode'] or False,
            worker=validated_data['worker'] or None,
            company=self.context['request'].user.company,
        )


class SendActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervisor
        fields = []

    def update(self, instance, validated_data):
        instance.is_active = True

        instance.save()

        return instance


class WorkerPresenceLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkerLogs
        fields = [
            "type",
            "description"
        ]

    def create(self, validated_data):
        supervisor = Supervisor.objects.get(serial_number=self.context['request'].META.get("HTTP_SERIAL_NUMBER"))
        supervisor_worker = supervisor.worker
        worker_curr_task = TaskAppointment.objects.filter(is_done=False, worker_appointed=supervisor_worker).first()
        if not supervisor_worker:
            raise serializers.ValidationError({'detail': _('The IoT does not have assigned worker!')})
        if not worker_curr_task:
            raise serializers.ValidationError({'detail': _('The assigned worker does not have task now!')})
        return WorkerLogs.objects.create(
            type=validated_data.get("type"),
            description=validated_data.get("description"),
            worker=supervisor_worker,
            task=worker_curr_task.task_appointed
        )
