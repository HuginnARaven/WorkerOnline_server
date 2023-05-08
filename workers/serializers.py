from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers

from companies.serializers import TaskSerializer, WorkerTaskCommentSerializer
from workers.models import TaskAppointment, WorkerLogs


class TaskDoneSerializer(serializers.ModelSerializer):
    task_info = TaskSerializer(read_only=True, source="task_appointed")
    difficulty_for_worker = serializers.FloatField(read_only=True)
    is_done = serializers.BooleanField(read_only=True)
    comments = WorkerTaskCommentSerializer(many=True, read_only=True)
    time_start = serializers.DateTimeField(read_only=True)
    time_end = serializers.DateTimeField(read_only=True)

    class Meta:
        model = TaskAppointment
        fields = [
            'id',
            'is_done',
            'comments',
            'time_start',
            'time_end',
            'difficulty_for_worker',
            'task_info',
        ]

    def update(self, instance, validated_data):
        if instance.is_done:
            raise serializers.ValidationError({'detail': [
                'Task already was done!'
            ]})

        instance.is_done = True
        instance.time_end = timezone.now()
        instance.save()

        return instance


class WorkersLogSerializer(serializers.ModelSerializer):
    task_info = TaskSerializer(read_only=True, source="task")
    localized_datetime = serializers.SerializerMethodField()

    class Meta:
        model = WorkerLogs
        fields = [
            'id',
            'date',
            'time',
            'localized_datetime',
            'type',
            'description',
            'task',
            'task_info',
        ]

    def get_localized_datetime(self, obj):
        localized_datetime = timezone.localtime(obj.datetime, obj.worker.employer.get_timezone())
        return localized_datetime.strftime('%Y-%m-%d %H:%M:%S')

