from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from companies.models import TaskVoting
from companies.serializers import TaskSerializer
from workers.models import TaskAppointment, WorkerLogs, WorkerTaskComment, TaskVote


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

    task_title = serializers.CharField(read_only=True, source="task_appointed.title")
    task_description = serializers.CharField(read_only=True, source="task_appointed.description")
    deadline = serializers.SerializerMethodField(read_only=True)
    task_is_done = serializers.CharField(read_only=True, source="task_appointed.is_done")
    task_estimate_hours = serializers.IntegerField(read_only=True, source="task_appointed.estimate_hours")

    comments = WorkerTaskCommentSerializer(many=True, read_only=True)
    time_start = serializers.SerializerMethodField(read_only=True)
    time_end = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TaskAppointment
        fields = [
            'id',
            'is_done',
            "status",
            'time_start',
            'time_end',
            'task_title',
            'task_description',
            'task_estimate_hours',
            'task_is_done',
            'deadline',
            'comments',
        ]

    def get_deadline(self, obj):
        localized_datetime = timezone.localtime(obj.deadline, obj.worker_appointed.employer.get_timezone())
        return localized_datetime.strftime('%Y-%m-%d %H:%M:%S')

    def get_time_start(self, obj):
        localized_datetime = timezone.localtime(obj.time_start, obj.worker_appointed.employer.get_timezone())
        return localized_datetime.strftime('%Y-%m-%d %H:%M:%S')

    def get_time_end(self, obj):
        if obj.time_end:
            localized_datetime = timezone.localtime(obj.time_end, obj.worker_appointed.employer.get_timezone())
            return localized_datetime.strftime('%Y-%m-%d %H:%M:%S')
        return ""

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
    localized_datetime = serializers.SerializerMethodField()

    class Meta:
        model = WorkerLogs
        fields = [
            'id',
            'datetime',
            'localized_datetime',
            'type',
            'description',
            'task',
        ]

    def get_localized_datetime(self, obj):
        localized_datetime = timezone.localtime(obj.datetime, obj.worker.employer.get_timezone())
        return localized_datetime.strftime('%Y-%m-%d %H:%M:%S')


class VoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskVote
        fields = [
            'id',
            'task',
            'score',
            'voting',
        ]

    def validate(self, data):
        worker = self.context['request'].user.worker
        errors = {}
        if data['task'] not in data['voting'].voting_tasks.all():
            errors.update({'task': ['You can not vote for this task in this voting!']})

        if data['voting'].company != worker.employer:
            errors.update({'voting': ['You can not vote in voting other company voting!']})

        if not data['voting'].is_active:
            errors.update({'voting': ['Voting already ended!']})

        if data['voting'].max_score < data['score'] or data['score'] < data['voting'].min_score:
            errors.update({'score': [f'Your score is not in scoring range! (min: {data["voting"].min_score} max: {data["voting"].max_score})']})

        if errors:
            raise serializers.ValidationError(errors)

        return data

    def create(self, validated_data):
        worker = self.context['request'].user.worker
        if TaskVote.objects.filter(task=validated_data['task'],
                                   voting=validated_data['voting'],
                                   worker=worker).exists():
            raise serializers.ValidationError({'worker': ['You have already voted!']})
        if TaskVote.objects.filter(score=validated_data['score'],
                                   voting=validated_data['voting'],
                                   worker=worker).exists():
            raise serializers.ValidationError({'worker': ['You have already voted with this score!']})
        return TaskVote.objects.create(
            task=validated_data["task"],
            score=validated_data["score"],
            voting=validated_data["voting"],
            worker=self.context['request'].user.worker
        )

    def update(self, instance, validated_data):
        worker = self.context['request'].user.worker
        if validated_data.get("task") and instance.task != validated_data.get("task"):
            raise serializers.ValidationError({'task': ['You can not edit task field!']})
        if validated_data.get("voting") and instance.voting != validated_data.get("voting"):
            raise serializers.ValidationError({'task': ['You can not edit voting field!']})
        if TaskVote.objects.filter(score=validated_data['score'],
                                   voting=validated_data['voting'],
                                   worker=worker).exclude(id=instance.id).exists():
            raise serializers.ValidationError({'worker': ['You have already voted with this score!']})

        instance.score = validated_data["score"] or instance.score
        instance.save()

        return instance


class GetVotingSerializer(serializers.ModelSerializer):
    voting_tasks = serializers.SerializerMethodField(read_only=True)
    voting_winner = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TaskVoting
        fields = [
            "id",
            "title",
            "description",
            "max_score",
            "min_score",
            "voting_tasks",
            "deadline",
            "is_active",
            "voting_tasks",
            "voting_winner",
        ]

    def get_voting_tasks(self, obj):
        tasks = obj.voting_tasks.all()
        result = []

        for task in tasks:
            user_vote = TaskVote.objects.filter(task=task, voting=obj, worker=self.context['request'].user.worker).first()
            if user_vote:
                result.append({"id": task.id, "title": task.title, "score": user_vote.score, "user_vote_id": user_vote.id})
            else:
                result.append({"id": task.id, "title": task.title, "score": 0, "user_vote_id": None})

        return result

    def get_voting_winner(self, obj):
        if not obj.is_active:
            tasks = obj.voting_tasks.all()
            votes = obj.votes.all()
            winner = ["", 0]
            for task in tasks:
                score = 0
                for vote in votes:
                    if vote.task == task:
                        expertness = vote.worker.qualification.modifier * vote.worker.productivity
                        score += vote.score * expertness
                if winner[1] < score:
                    winner = [task.title, score]

            return winner[0]

        return "There are no winner at that time!"
