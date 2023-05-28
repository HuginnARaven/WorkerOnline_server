from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from companies.serializers import TaskSerializer
from workers.models import TaskAppointment, WorkerLogs, WorkerTaskComment


class WorkerTaskCommentSerializer(serializers.ModelSerializer):
    time_created = serializers.DateTimeField(read_only=True)
    username = serializers.CharField(read_only=True, source='user.username')

    class Meta:
        model = WorkerTaskComment
        fields = [
            'id',
            'username',
            'text',
            'time_created',
            'task_appointment',
        ]

    def validate(self, data):
        if data.get('task_appointment') and not TaskAppointment.objects.filter(id=data.get('task_appointment').id,
                                                                               worker_appointed=self.context[
                                                                                   'request'].user.worker):
            raise serializers.ValidationError({'task_appointment': [
                _('The task_appointment does not exist or does not belong to your!')
            ]})

        return data

    def update(self, instance, validated_data):
        errors = {}
        if validated_data.get('task_appointment') and validated_data.get(
                'task_appointment') != instance.task_appointment:
            errors.update({'task_appointment': [_('You can not change task for comment!')]})

        if self.context['request'].user != instance.user:
            errors.update({'user': [_('You can not change another people comments!')]})

        if errors:
            raise serializers.ValidationError(errors)

        instance.text = validated_data.get('text') or instance.text
        instance.save()

        return instance

    def create(self, validated_data):
        return WorkerTaskComment.objects.create(
            text=validated_data['text'],
            task_appointment=validated_data['task_appointment'],
            user=self.context['request'].user
        )


class TaskDoneSerializer(serializers.ModelSerializer):
    task_info = TaskSerializer(read_only=True, source="task_appointed")
    difficulty_for_worker = serializers.FloatField(read_only=True)
    comments = WorkerTaskCommentSerializer(many=True, read_only=True)
    time_start = serializers.DateTimeField(read_only=True)
    time_end = serializers.DateTimeField(read_only=True)

    class Meta:
        model = TaskAppointment
        fields = [
            'id',
            'is_done',
            "status",
            'comments',
            'time_start',
            'time_end',
            'difficulty_for_worker',
            'task_info',
        ]

    def update(self, instance, validated_data):
        if instance.is_done:
            raise serializers.ValidationError({'is_done': [
                'Task already was done, you can`t change it!'
            ]})
        is_done = validated_data.get("is_done") or instance.is_done
        instance.is_done = is_done
        initial_status = instance.status
        if is_done:
            instance.time_end = timezone.now()
        instance.status = validated_data.get("status") or instance.status

        if is_done or validated_data.get("status") != initial_status:
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
