from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from companies.models import Company
from users.models import UserAccount, TechSupportRequest
from workers.models import Worker


class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAccount
        fields = '__all__'


class CompanyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = [
            'username',
            'email',
            'name',
            'description',
            'timezone',
        ]


class WorkerProfileSerializer(serializers.ModelSerializer):
    worker_qualification = serializers.CharField(read_only=True, source="qualification.name")
    worker_salary = serializers.IntegerField(read_only=True, source="salary")
    worker_day_start = serializers.TimeField(read_only=True, source="day_start")
    worker_day_end = serializers.TimeField(read_only=True, source="day_end")

    class Meta:
        model = Worker
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'worker_qualification',
            'worker_day_start',
            'worker_day_end',
            'worker_salary',
        ]


class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = UserAccount
        fields = ('old_password', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": _("New password fields didn't match")})

        return attrs

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(_("Old password is not correct"))
        return value

    def update(self, instance, validated_data):

        instance.set_password(validated_data['password'])
        instance.save()

        return instance


class TechSupportRequestSerializer(serializers.ModelSerializer):
    admin_response = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True, source='get_status_display')
    localized_created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = TechSupportRequest
        fields = [
            'id',
            'title',
            'description',
            'admin_response',
            'status',
            'localized_created_at',
        ]

    def get_localized_created_at(self, obj):
        if obj.user.role == 'C':
            localized_datetime = timezone.localtime(obj.time_created, obj.user.company.get_timezone())
        elif obj.user.role == 'W':
            localized_datetime = timezone.localtime(obj.time_created, obj.user.worker.emploer.get_timezone())
        else:
            localized_datetime = obj.time_created

        return localized_datetime.strftime('%Y-%m-%d %H:%M:%S')

    def create(self, validated_data):
        if TechSupportRequest.objects.filter(user=self.context['request'].user, status='CR').count() >= 3:
            raise serializers.ValidationError({'detail': [_('You have too many unread requests!')]})
        return TechSupportRequest.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            user=self.context['request'].user,
        )

    def update(self, instance, validated_data):
        errors = {}
        if validated_data.get('title') and instance.status != 'CR':
            errors.update({'title': [_('You can not change title of request when it is viewed or closed!')]})

        if validated_data.get('description') and instance.status != 'CR':
            errors.update({'description': [_('You can not change description of request when it is viewed or closed!')]})

        if errors:
            raise serializers.ValidationError(errors)

        instance.title = validated_data.get('title') or instance.title
        instance.description = validated_data.get('description') or instance.description

        instance.save()

        return instance
