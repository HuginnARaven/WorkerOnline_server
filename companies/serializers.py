import datetime

import pytz
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.db.models import F

from companies.models import Company, Qualification, Task
from workers.models import Worker, TaskAppointment, WorkerLogs, WorkerTaskComment, WorkerSchedule


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
            raise serializers.ValidationError({'password': [_('Passwords do not match!')]})
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

    def validate(self, data):
        errors = {}

        if data.get('difficulty') and self.context['request'].user.company != data['difficulty'].company:
            errors.update({'qualification': [_('You cannot use another company`s qualifications!')]})

        if errors:
            raise serializers.ValidationError(errors)

        return data

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
            raise serializers.ValidationError({'task_appointed': [_('You can not edit appointed task!')]})

        instance.title = validated_data.get('title') or instance.title
        instance.description = validated_data.get('description') or instance.description
        instance.estimate_hours = validated_data.get('estimate_hours') or instance.estimate_hours
        instance.difficulty = validated_data.get('difficulty') or instance.difficulty

        return instance


class WorkerScheduleSerializer(serializers.ModelSerializer):
    worker_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = WorkerSchedule
        fields = [
            "id",
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
            "worker_id"
        ]


class WorkerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True, validators=[validate_password])
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    worker_qualification_info = QualificationSerializer(read_only=True, source="qualification")
    worker_schedule = WorkerScheduleSerializer(read_only=True, source="schedule")
    id = serializers.IntegerField(read_only=True)

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
            'worker_schedule',
        ]

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        errors = {}

        if password and password != password2:
            errors.update({'password': [_('Passwords do not match!')]})
        if data.get('qualification') and self.context['request'].user.company != data['qualification'].company:
            errors.update({'qualification': [_('You cannot use another company`s qualifications!')]})

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):

        return Worker.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            password=make_password(validated_data['password']),
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


class CompanyTaskCommentSerializer(serializers.ModelSerializer):
    time_created = serializers.DateTimeField(read_only=True)
    username = serializers.CharField(read_only=True, source='user.username')
    localized_time_created = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = WorkerTaskComment
        fields = [
            'id',
            'username',
            'text',
            'time_created',
            'localized_time_created',
            'task_appointment',
        ]

    def validate(self, data):
        if data.get('task_appointment') and not TaskAppointment.objects.filter(id=data.get('task_appointment').id, task_appointed__company=self.context['request'].user.company):
            raise serializers.ValidationError({'task_appointment': [
                _('The task_appointment does not exist or does not belong to your company!')
            ]})

        return data

    def get_localized_time_created(self, obj):
        print(obj.user.role)
        if obj.user.role == 'C':
            localized_datetime = timezone.localtime(obj.time_created, obj.user.company.get_timezone())
        else:
            localized_datetime = timezone.localtime(obj.time_created, obj.user.worker.employer.get_timezone())
        return localized_datetime.strftime('%Y-%m-%d %H:%M:%S')

    def update(self, instance, validated_data):
        if validated_data.get('task_appointment') and validated_data.get('task_appointment') != instance.task_appointment:
            raise serializers.ValidationError({'task_appointment': [_('You can not change task for comment!')]})

        if self.context['request'].user != instance.user:
            raise serializers.ValidationError({'user': [_('You can not change another people comments!')]})

        instance.text = validated_data.get('text') or instance.text

        instance.save()

        return instance

    def create(self, validated_data):
        return WorkerTaskComment.objects.create(
            text=validated_data['text'],
            task_appointment=validated_data['task_appointment'],
            user=self.context['request'].user
        )


class TaskAppointmentSerializer(serializers.ModelSerializer):
    task_info = TaskSerializer(read_only=True, source="task_appointed")
    worker_info = WorkerSerializer(read_only=True, source="worker_appointed")
    is_done = serializers.BooleanField(read_only=True)
    difficulty_for_worker = serializers.FloatField(read_only=True)
    time_start = serializers.DateTimeField(read_only=True)
    time_end = serializers.DateTimeField(read_only=True)
    status = serializers.CharField(read_only=True)
    comments = CompanyTaskCommentSerializer(many=True, read_only=True)

    class Meta:
        model = TaskAppointment
        fields = [
            'id',
            'is_done',
            'status',
            'comments',
            'time_start',
            'time_end',
            'difficulty_for_worker',
            'task_appointed',
            'task_info',
            'worker_appointed',
            'worker_info',
            'deadline',
        ]

    def validate(self, data):
        errors = {}

        if not Worker.objects.filter(id=data['worker_appointed'].id, employer=self.context['request'].user.company):
            errors.update(
                {'worker_appointed': [_('The assigned worker does not exist or does not belong to your company!')]})
        if not Task.objects.filter(id=data['task_appointed'].id,
                                   company=self.context['request'].user.company):
            errors.update({'task_appointed': [
                _('The assigned task does not exist or does not belong to your company!')
            ]})

        if errors:
            raise serializers.ValidationError(errors)

        if data['task_appointed'].difficulty.modifier > data['worker_appointed'].qualification.modifier:
            errors.update({'difficulty': [
                _('There is higher difficulty of the task then employee can handle!')
            ]})
        if data['task_appointed'].estimate_hours > data['worker_appointed'].working_hours:
            errors.update({'estimated_hours': [
                _('There are more estimated hours of the task then the working hours of the employee per week!')
            ]})

        if TaskAppointment.objects.filter(worker_appointed=data['worker_appointed'], is_done=False):
            errors.update({'worker_appointed': [
                _('The appointed worker already has active task!')
            ]})

        if TaskAppointment.objects.filter(task_appointed=data['task_appointed']):
            errors.update({'task_appointed': [
                _('This task has been appointed already!')
            ]})

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        return TaskAppointment.objects.create(
            task_appointed=validated_data['task_appointed'],
            worker_appointed=validated_data['worker_appointed'],
            deadline=validated_data["deadline"].astimezone(pytz.utc)
        )

    def update(self, instance, validated_data):
        instance.task_appointed = validated_data.get('task_appointed') or instance.task_appointed
        instance.worker_appointed = validated_data.get('worker_appointed') or instance.worker_appointed

        instance.save()

        return instance


class WorkerLogSerializer(serializers.ModelSerializer):
    datetime = serializers.DateTimeField(read_only=True)
    localized_datetime = serializers.SerializerMethodField()

    class Meta:
        model = WorkerLogs
        fields = [
            'id',
            'datetime',
            'localized_datetime',
            'type',
            'description',
            'worker',
            'task',
        ]

    def get_localized_datetime(self, obj):
        localized_datetime = timezone.localtime(obj.datetime, obj.worker.employer.get_timezone())
        return localized_datetime.strftime('%Y-%m-%d %H:%M:%S')


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
        workers = sorted(workers, key=lambda a: a.count_remaining_working_hours(), reverse=True)
        for worker in workers:
            if not TaskAppointment.objects.filter(is_done=False, worker_appointed=worker):
                result.append({
                    "id": worker.id,
                    "first_name": worker.first_name,
                    "last_name": worker.last_name,
                    "productivity": worker.productivity,
                    "working_hours": worker.working_hours,
                    "approx_finsh_date": worker.get_recommended_deadline_for_task(obj, datetime.datetime.now(tz=worker.employer.get_timezone())),
                })

        if not result:
            return _('There are no workers to recommend for this task for now! (probably some workers that can be recommended are busy now)')
        return result


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
        if not self.context['request'].query_params.get("days"):
            worker_logs = WorkerLogs.objects.filter(worker=obj)
            times_deadline_not_met = TaskAppointment.objects.filter(worker_appointed=obj,
                                                                    is_done=True,
                                                                    deadline__gt=F('time_end')).count()
        else:
            days = timezone.now() - datetime.timedelta(days=int(self.context['request'].query_params.get("days")))
            worker_logs = WorkerLogs.objects.filter(worker=obj, datetime__gte=days)
            times_deadline_not_met = TaskAppointment.objects.filter(worker_appointed=obj,
                                                                    is_done=True,
                                                                    deadline__gt=F('time_end'),
                                                                    time_end__gte=days).count()

        result = {
            "tasks_done": worker_logs.filter(type__exact="TD").count(),
            "times_out_of_working_place": worker_logs.filter(type__exact="OC").count(),
            "times_deadline_not_met": times_deadline_not_met
        }

        return result

    def get_worker_tasks_statistics(self, obj):
        days = self.context['request'].query_params.get("days")
        if days:
            days = timezone.now() - datetime.timedelta(days=int(days))
            worker_tasks_appointments = TaskAppointment.objects.filter(worker_appointed=obj,
                                                                       is_done=True,
                                                                       time_end__gte=days)
        else:
            worker_tasks_appointments = TaskAppointment.objects.filter(worker_appointed=obj,
                                                                       is_done=True)

        result = []
        for task_appointment in worker_tasks_appointments:
            logs = WorkerLogs.objects.filter(task=task_appointment.task_appointed)
            result.append({
                "title": task_appointment.task_appointed.title,
                "estimate_hours": task_appointment.task_appointed.estimate_hours,
                "times_out_of_working_place": logs.filter(type__exact="OC").count(),
                "task_performance": task_appointment.get_task_performance(),
                "is_deadline_met": (task_appointment.deadline < task_appointment.time_end),
                "spent_working_hours": (task_appointment.task_appointed.estimate_hours / task_appointment.get_task_performance()),
                "time_start": timezone.localtime(task_appointment.time_start, task_appointment.worker_appointed.employer.get_timezone()).strftime('%Y-%m-%d %H:%M:%S'),
                "time_end": timezone.localtime(task_appointment.time_end, task_appointment.worker_appointed.employer.get_timezone()).strftime('%Y-%m-%d %H:%M:%S'),
                "deadline": task_appointment.deadline
            })

        return result


class AutoAppointmentSerializer(serializers.ModelSerializer):
    workers = serializers.SerializerMethodField(read_only=True)
    tasks = serializers.SerializerMethodField(read_only=True)
    previous_appointments = serializers.SerializerMethodField(read_only=True)
    new_appointments = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Company
        fields = [
            "tasks",
            "workers",
            "previous_appointments",
            "new_appointments",
        ]

    def get_workers(self, obj):
        workers = Worker.objects.filter(employer=obj).order_by("-productivity", "qualification__modifier", "working_hours")
        result = []
        for worker in workers:
            result.append({
                "id": worker.id,
                "username": worker.username,
                "working_hours": worker.working_hours,
                "qualification_modifier": worker.qualification.modifier,
                "productivity": worker.productivity,
            })

        return result

    def get_tasks(self, obj):
        tasks = Task.objects.filter(company=obj)
        result = []
        for task in tasks:
            result.append({
                "id": task.id,
                "title": task.title,
                "estimate_hours": task.estimate_hours,
                "difficulty_modifier": task.difficulty.modifier,
            })

        return result

    def get_previous_appointments(self, obj):
        appointments = TaskAppointment.objects.filter(task_appointed__company=obj)
        result = []
        for appointment in appointments:
            result.append({
                "task_id": appointment.task_appointed_id,
                "worker_id": appointment.worker_appointed_id,
            })

        return result

    def get_new_appointments(self, obj):
        is_save_mode = self.context['request'].query_params.get("is_save_mode") != 'false'
        sorted_workers = Worker.objects.filter(employer=obj).order_by("-productivity", "qualification__modifier", "working_hours")
        tasks = Task.objects.filter(company=obj)
        assigned_tasks = []
        assignment_steps = []
        assigned_workers = set()

        result = {
            "assigned_tasks": assigned_tasks,
            "steps": assignment_steps
        }

        i = 0
        for task in tasks:
            if not TaskAppointment.objects.filter(task_appointed=task):
                chosen_worker = None

                for worker in sorted_workers:
                    if not TaskAppointment.objects.filter(is_done=False, worker_appointed=worker) \
                            and worker not in assigned_workers \
                            and task.difficulty.modifier <= worker.qualification.modifier \
                            and task.estimate_hours <= worker.working_hours:
                        chosen_worker = worker
                        break

                if chosen_worker:
                    if i == 0:
                        assignment_steps.append({
                            "step": i,
                            "assigned_tasks": []
                        })
                    i = i + 1
                    if not is_save_mode:
                        TaskAppointment.objects.create(worker_appointed=chosen_worker,
                                                       task_appointed=task,
                                                       deadline=chosen_worker.get_recommended_deadline_for_task(task, timezone.now()))
                    assigned_tasks.append({
                        "task_id": task.id,
                        "worker_id": chosen_worker.id
                    })
                    assignment_steps.append({
                        "step": i,
                        "assigned_tasks": list(assigned_tasks)
                    })
                    assigned_workers.add(chosen_worker)

        return result
