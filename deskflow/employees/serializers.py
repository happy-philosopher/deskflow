from rest_framework import serializers
from .models import EmployeeProfile, EmployeeSkill, EmployeeImage, Skill
from desks.models import Desk


class EmployeeSkillSerializer(serializers.ModelSerializer):
    skill_name = serializers.CharField(source='skill.name', read_only=True)

    class Meta:
        model = EmployeeSkill
        fields = ['skill', 'skill_name', 'level']


class EmployeeImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeImage
        fields = ['id', 'image', 'order']


class EmployeeProfileSerializer(serializers.ModelSerializer):
    skills = EmployeeSkillSerializer(source='employee_skills', many=True, read_only=True)
    images = EmployeeImageSerializer(many=True, read_only=True)
    desk_number = serializers.CharField(source='desk.number', read_only=True)

    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Описание сотрудника (может быть пустым)"
    )

    class Meta:
        model = EmployeeProfile
        fields = [
            'id', 'user', 'first_name', 'last_name', 'middle_name',
            'gender', 'description', 'hire_date',
            'created_at', 'updated_at',
            'desk_number', 'skills', 'images'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']