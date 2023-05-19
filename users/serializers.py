from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from companies.models import Company
from users.models import UserAccount
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
            raise serializers.ValidationError(_("Password fields didn't match"))

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

