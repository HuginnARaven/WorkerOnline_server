from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from companies.models import Company, Qualification
from workers.models import Worker


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


class WorkerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True, validators=[validate_password])
    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    worker_qualification_info = QualificationSerializer(read_only=True, source="qualification")
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
            day_start=validated_data['day_start'],
            day_end=validated_data['day_end'],
            salary=validated_data['salary'],
        )

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        password2 = validated_data.get('password2')
        if password != password2:
            raise serializers.ValidationError({'detail': ['Password do not match!']})
        if self.context['request'].user.company != validated_data.get('qualification').company:
            raise serializers.ValidationError({'detail': ['You cannot use another company`s qualifications!']})

        instance.username = validated_data.get('username')
        instance.email = validated_data.get('email')
        instance.password = make_password(password)
        instance.first_name = validated_data.get('first_name')
        instance.last_name = validated_data.get('last_name')
        instance.qualification = validated_data.get('qualification')
        instance.day_start = validated_data.get('day_start')
        instance.day_end = validated_data.get('day_end')
        instance.salary = validated_data.get('salary')

        return instance

