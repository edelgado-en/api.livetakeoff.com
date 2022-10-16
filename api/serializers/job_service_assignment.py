from rest_framework import serializers
from ..models import (
    JobServiceAssignment,
    JobRetainerServiceAssignment
    )

from .basic_user import BasicUserSerializer

class ChecklistActionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class GenericServiceAssignmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    status = serializers.CharField()
    checklist_actions = ChecklistActionSerializer(many=True)


class JobServiceAssignmentSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    project_manager = BasicUserSerializer()

    class Meta:
        model = JobServiceAssignment
        fields = ['id', 'status', 'project_manager']

class JobRetainerServiceAssignmentSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    project_manager = BasicUserSerializer()

    class Meta:
        model = JobRetainerServiceAssignment
        fields = ['id', 'status', 'project_manager']