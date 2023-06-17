from django.utils import timezone
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from iot.models import Supervisor, Offer
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
    in_admin_mode = serializers.BooleanField(read_only=True)
    last_active = serializers.DateTimeField(read_only=True)
    username = serializers.CharField(read_only=True, source="worker.username")
    localized_last_active = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Supervisor
        fields = [
            "id",
            "in_admin_mode",
            "worker",
            "username",
            "is_active",
            "last_active",
            "localized_last_active"
        ]

    def get_localized_last_active(self, obj):
        localized_datetime = timezone.localtime(obj.last_active, obj.company.get_timezone())
        return localized_datetime.strftime('%Y-%m-%d %H:%M:%S')

    def validate(self, data):
        if data.get('worker'):
            if not Worker.objects.filter(id=data['worker'].id,
                                         employer=self.context['request'].user.company):
                raise serializers.ValidationError({'worker': [
                    _('The assigned worker does not exist or belong to your company!')
                ]})
            if Supervisor.objects.filter(worker=data['worker']):
                raise serializers.ValidationError({'worker': [
                    _('The assigned worker already have Supervisor!')
                ]})

        return data

    def create(self, validated_data):
        return Supervisor.objects.create(
            in_admin_mode=validated_data['in_admin_mode'] or False,
            worker=validated_data['worker'] or None,
            company=self.context['request'].user.company,
        )


class OfferSerializer(serializers.ModelSerializer):
    status = serializers.CharField(read_only=True, source='get_status_display')
    localized_created_at = serializers.SerializerMethodField(read_only=True)
    last_changed = serializers.DateTimeField(read_only=True)
    localized_last_changed = serializers.SerializerMethodField(read_only=True)
    comment = serializers.CharField(read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "status",
            "created_at",
            "localized_created_at",
            "last_changed",
            "localized_last_changed",
            "address_of_delivery",
            "comment",
        ]

    def get_localized_created_at(self, obj):
        localized_datetime = timezone.localtime(obj.created_at, obj.company.get_timezone())
        return localized_datetime.strftime('%Y-%m-%d %H:%M:%S')

    def get_localized_last_changed(self, obj):
        localized_datetime = timezone.localtime(obj.last_changed, obj.company.get_timezone())
        return localized_datetime.strftime('%Y-%m-%d %H:%M:%S')

    def create(self, validated_data):
        return Offer.objects.create(
            address_of_delivery=validated_data['address_of_delivery'],
            company=self.context['request'].user.company,
        )

    def update(self, instance, validated_data):
        if validated_data.get('address_of_delivery') and validated_data.get('address_of_delivery') != instance.address_of_delivery and instance.status not in ['CR', 'RC', 'IC']:
            raise serializers.ValidationError({'address_of_delivery': [_('You can not change address of delivery for offer at that stage!')]})

        instance.address_of_delivery = validated_data.get('address_of_delivery') or instance.address_of_delivery

        instance.save()

        return instance


class SendActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervisor
        fields = []

    def update(self, instance, validated_data):
        instance.is_active = True
        instance.last_active = timezone.now()

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


class SupervisorServerTimeSerializer(serializers.ModelSerializer):
    server_time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Supervisor
        fields = [
            "server_time",
        ]

    def get_server_time(self, obj):
        localized_now = timezone.localtime(timezone.now(), obj.company.get_timezone())
        return localized_now.strftime('%H:%M:%S')
