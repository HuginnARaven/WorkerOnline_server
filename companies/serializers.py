import datetime

from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from rest_framework.fields import Field

from companies.models import Company, Qualification, Task
from workers.models import Worker, WorkersTasks, WorkerLogs


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
            raise serializers.ValidationError({'detail': ['Password do not match!']})
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
        if WorkersTasks.objects.filter(task_appointed=instance.id):
            raise serializers.ValidationError({'detail': ['You can not edit appointed task!']})

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
            raise serializers.ValidationError({'detail': ['Password do not match!']})
        if self.context['request'].user.company != validated_data['qualification'].company:
            raise serializers.ValidationError({'detail': ['You cannot use another company`s qualifications!']})

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
        model = WorkersTasks
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
                'The assigned worker does not exist or does not belong to your company!'
            ]})
        if not Task.objects.filter(id=data['task_appointed'].id,
                                   company=self.context['request'].user.company):
            raise serializers.ValidationError({'detail': [
                'The assigned task does not exist or does not belong to your company!'
            ]})
        if data['task_appointed'].difficulty.modifier > data['worker_appointed'].qualification.modifier:
            raise serializers.ValidationError({'detail': [
                'There is higher difficulty of the task then employee can handle!'
            ]})
        if data['task_appointed'].estimate_hours > data['worker_appointed'].working_hours:
            raise serializers.ValidationError({'detail': [
                'There are more estimated hours of the task then the working hours of the employee per week!'
            ]})

        return data

    def create(self, validated_data):
        if WorkersTasks.objects.filter(worker_appointed=validated_data['worker_appointed'], is_done=False):
            raise serializers.ValidationError({'detail': [
                'The appointed worker already has active task!'
            ]})

        if WorkersTasks.objects.filter(task_appointed=validated_data['task_appointed']):
            raise serializers.ValidationError({'detail': [
                'This task has been appointed already!'
            ]})

        return WorkersTasks.objects.create(
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

    class Meta:
        model = WorkerLogs
        fields = [
            'id',
            'date',
            'time',
            'type',
            'description',
            'worker',
            'worker_info',
            'task',
            'task_info',
        ]
