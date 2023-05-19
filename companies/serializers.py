import datetime

import pytz
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework.fields import Field
from django.core import serializers as core_serializers
from django.utils.translation import gettext_lazy as _

from companies.models import Company, Qualification, Task
from workers.models import Worker, TaskAppointment, WorkerLogs, WorkerTaskComment


class CompanySerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True, validators=[validate_password])
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = Company
        fields = [
            'username',
            'email',
            'password',
            'password2',
            'name',
            'description',
        ]

    def create(self, validated_data):
        password = validated_data['password']
        password2 = validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'detail': [_('Password do not match!')]})
        return Company.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            password=make_password(password),
            role='C',
            name=validated_data['name'],
            description=validated_data['description'],
        )


class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualification
        fields = [
            'id',
            'name',
            'modifier',
        ]

    def create(self, validated_data):
        return Qualification.objects.create(
            name=validated_data['name'],
            modifier=validated_data['modifier'],
            company=self.context['request'].user.company,
        )


class TaskSerializer(serializers.ModelSerializer):
    task_difficulty_info = QualificationSerializer(read_only=True, source="difficulty")

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'estimate_hours',
            'difficulty',
            'task_difficulty_info',
        ]

    def create(self, validated_data):
        return Task.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            estimate_hours=validated_data['estimate_hours'],
            difficulty=validated_data['difficulty'],
            company=self.context['request'].user.company,
        )

    def update(self, instance, validated_data):
        if TaskAppointment.objects.filter(task_appointed=instance.id):
            raise serializers.ValidationError({'detail': [_('You can not edit appointed task!')]})

        instance.title = validated_data.get('title')
        instance.description = validated_data.get('description')
        instance.estimate_hours = validated_data.get('estimate_hours')
        instance.difficulty = validated_data.get('difficulty')

        return instance


# class TimeWithTimezoneField(Field):
#
#     default_error_messages = {
#         'invalid': 'Time has wrong format, expecting %H:%M:%S%z.',
#     }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     def to_internal_value(self, value):
#         try:
#             parsed = datetime.datetime.combine(date=datetime.date.today(),
#                                                time=datetime.datetime.strptime(value, "%H:%M:%S").time(),
#                                                tzinfo=self.context['request'].user.company.get_timezone())
#         except (ValueError, TypeError) as e:
#             pass
#         else:
#             return parsed
#         self.fail('invalid')
#
#     def to_representation(self, value):
#         if not value:
#             return None
#
#         if isinstance(value, str):
#             return value
#         return timezone.make_naive(value, self.context['request'].user.company.get_timezone()).strftime("%H:%M:%S%z")


class WorkerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True, validators=[validate_password])
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    worker_qualification_info = QualificationSerializer(read_only=True, source="qualification")
    id = serializers.IntegerField(read_only=True)
    # day_start = TimeWithTimezoneField()
    # day_end = TimeWithTimezoneField()

    class Meta:
        model = Worker
        fields = [
            'id',
            'username',
            'email',
            'password',
            'password2',
            'first_name',
            'last_name',
            'qualification',
            'worker_qualification_info',
            'working_hours',
            'day_start',
            'day_end',
            'salary',
        ]

    def create(self, validated_data):
        password = validated_data['password']
        password2 = validated_data['password2']
        if password != password2:
            raise serializers.ValidationError({'detail': [_('Password do not match!')]})
        if self.context['request'].user.company != validated_data['qualification'].company:
            raise serializers.ValidationError({'detail': [_('You cannot use another company`s qualifications!')]})

        return Worker.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            password=make_password(password),
            role='W',
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            employer=self.context['request'].user.company,
            qualification=validated_data['qualification'],
            working_hours=validated_data['working_hours'],
            day_start=validated_data['day_start'],
            day_end=validated_data['day_end'],
            salary=validated_data['salary'],
        )


    def update(self, instance, validated_data):
        password = validated_data.get('password')
        password2 = validated_data.get('password2')
        if password != password2:
            raise serializers.ValidationError({'detail': ['Password do not match!']})
        # if self.context['request'].user.company != validated_data.get('qualification').company:
        #     raise serializers.ValidationError({'detail': ['You cannot use another company`s qualifications!']})

        instance.username = validated_data.get('username') or instance.username
        instance.email = validated_data.get('email') or instance.email
        instance.password = make_password(password) or instance.password
        instance.first_name = validated_data.get('first_name') or instance.first_name
        instance.last_name = validated_data.get('last_name') or instance.last_name
        instance.qualification = validated_data.get('qualification') or instance.qualification
        instance.working_hours = validated_data.get('working_hours') or instance.working_hours
        instance.day_start = validated_data.get('day_start') or instance.day_start
        instance.day_end = validated_data.get('day_end') or instance.day_end
        instance.salary = validated_data.get('salary') or instance.salary

        instance.save()

        return instance


class TaskAppointmentSerializer(serializers.ModelSerializer):
    task_info = TaskSerializer(read_only=True, source="task_appointed")
    worker_info = WorkerSerializer(read_only=True, source="worker_appointed")
    is_done = serializers.BooleanField(read_only=True)
    difficulty_for_worker = serializers.FloatField(read_only=True)
    time_start = serializers.DateTimeField(read_only=True)
    time_end = serializers.DateTimeField(read_only=True)

    class Meta:
        model = TaskAppointment
        fields = [
            'id',
            'is_done',
            'time_start',
            'time_end',
            'difficulty_for_worker',
            'task_appointed',
            'task_info',
            'worker_appointed',
            'worker_info',
        ]

    def validate(self, data):
        if not Worker.objects.filter(id=data['worker_appointed'].id,
                                     employer=self.context['request'].user.company):
            raise serializers.ValidationError({'detail': [
                _('The assigned worker does not exist or does not belong to your company!')
            ]})
        if not Task.objects.filter(id=data['task_appointed'].id,
                                   company=self.context['request'].user.company):
            raise serializers.ValidationError({'detail': [
                _('The assigned task does not exist or does not belong to your company!')
            ]})
        if data['task_appointed'].difficulty.modifier > data['worker_appointed'].qualification.modifier:
            raise serializers.ValidationError({'detail': [
                _('There is higher difficulty of the task then employee can handle!')
            ]})
        if data['task_appointed'].estimate_hours > data['worker_appointed'].working_hours:
            raise serializers.ValidationError({'detail': [
                _('There are more estimated hours of the task then the working hours of the employee per week!')
            ]})

        return data

    def create(self, validated_data):
        if TaskAppointment.objects.filter(worker_appointed=validated_data['worker_appointed'], is_done=False):
            raise serializers.ValidationError({'detail': [
                _('The appointed worker already has active task!')
            ]})

        if TaskAppointment.objects.filter(task_appointed=validated_data['task_appointed']):
            raise serializers.ValidationError({'detail': [
                _('This task has been appointed already!')
            ]})

        return TaskAppointment.objects.create(
            task_appointed=validated_data['task_appointed'],
            worker_appointed=validated_data['worker_appointed'],
        )

    def update(self, instance, validated_data):
        instance.task_appointed = validated_data.get('task_appointed') or instance.task_appointed
        instance.worker_appointed = validated_data.get('worker_appointed') or instance.worker_appointed

        instance.save()

        return instance


class WorkerLogSerializer(serializers.ModelSerializer):
    task_info = TaskSerializer(read_only=True, source="task")
    worker_info = WorkerSerializer(read_only=True, source="worker")
    datetime = serializers.DateTimeField(read_only=True)
    localized_datetime = serializers.SerializerMethodField()

    class Meta:
        model = WorkerLogs
        fields = [
            'id',
            'date',
            'time',
            'datetime',
            'localized_datetime',
            'type',
            'description',
            'worker',
            'worker_info',
            'task',
            'task_info',
        ]

    def get_localized_datetime(self, obj):
        localized_datetime = timezone.localtime(obj.datetime, obj.worker.employer.get_timezone())
        return localized_datetime.strftime('%Y-%m-%d %H:%M:%S')


class WorkerTaskCommentSerializer(serializers.ModelSerializer):
    time_created = serializers.DateTimeField(read_only=True)

    class Meta:
        model = WorkerTaskComment
        fields = [
            'id',
            'text',
            'time_created',
            'task_appointment',
        ]

    def validate(self, data):
        if data.get('task_appointment') and not TaskAppointment.objects.filter(id=data.get('task_appointment').id, task_appointed__company=self.context['request'].user.company):
            raise serializers.ValidationError({'task_appointment': [
                _('The task_appointment does not exist or does not belong to your company!')
            ]})

        return data

    def update(self, instance, validated_data):
        if validated_data.get('task_appointment') and validated_data.get('task_appointment') != instance.task_appointment:
            raise serializers.ValidationError({'task_appointment': [_('You can not change task for comment!')]})

        instance.text = validated_data.get('text') or instance.text

        instance.save()

        return instance


class TaskRecommendationSerializer(serializers.ModelSerializer):
    recommended_workers = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'recommended_workers',
        ]

    def get_recommended_workers(self, obj):
        estimate_hours = obj.estimate_hours
        difficulty = obj.difficulty
        company = obj.company
        workers = Worker.objects.filter(working_hours__gte=estimate_hours,
                                        qualification=difficulty,
                                        employer=company).order_by("-productivity")

        if not workers:
            workers = Worker.objects.filter(working_hours__gte=estimate_hours,
                                            qualification__modifier__gte=difficulty.modifier,
                                            employer=company).order_by("-productivity")
        if not workers:
            return _('There are no workers to recommend for this task!')
        result = []
        for worker in workers:
            if not TaskAppointment.objects.filter(is_done=False, worker_appointed=worker):
                result.append({
                    "id": worker.id,
                    "first_name": worker.first_name,
                    "last_name": worker.last_name,
                    "productivity": worker.productivity,
                    "working_hours": worker.working_hours,
                })

        if not result:
            return _('There are no workers to recommend for this task for now! (probably some workers that can be recommended are busy now)')
        return result
        # workers_serialize = core_serializers.serialize('python', workers)
        # workers_serialize_result = []
        # for worker in workers_serialize:
        #     if not TaskAppointment.objects.filter(is_done=False, worker_appointed_id=int(worker.get("pk"))):
        #         workers_serialize_result.append(worker.get("fields"))
        # return workers_serialize_result


class WorkerReportSerializer(serializers.ModelSerializer):
    worker_general_statistics = serializers.SerializerMethodField()
    worker_tasks_statistics = serializers.SerializerMethodField()

    class Meta:
        model = Worker
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            "worker_general_statistics",
            "worker_tasks_statistics",
        ]

    def get_worker_general_statistics(self, obj):
        worker_logs = WorkerLogs.objects.filter(worker=obj)
        result = {
            "tasks_done": worker_logs.filter(type__exact="TD").count(),
            "times_out_of_working_place": worker_logs.filter(type__exact="OC").count()
        }

        return result

    def get_worker_tasks_statistics(self, obj):
        worker_tasks_appointments = TaskAppointment.objects.filter(worker_appointed=obj, is_done=True)

        result = []
        for task_appointment in worker_tasks_appointments:
            logs = WorkerLogs.objects.filter(task=task_appointment.task_appointed)
            result.append({
                "title": task_appointment.task_appointed.title,
                "estimate_hours": task_appointment.task_appointed.estimate_hours,
                "times_out_of_working_place": logs.filter(type__exact="OC").count(),
                "task_performance": task_appointment.get_task_performance(),
                "spent_working_hours": (task_appointment.task_appointed.estimate_hours / task_appointment.get_task_performance()),
                "time_start": timezone.localtime(task_appointment.time_start, task_appointment.worker_appointed.employer.get_timezone()).strftime('%Y-%m-%d %H:%M:%S'),
                "time_end": timezone.localtime(task_appointment.time_end, task_appointment.worker_appointed.employer.get_timezone()).strftime('%Y-%m-%d %H:%M:%S')
            })

        return result
