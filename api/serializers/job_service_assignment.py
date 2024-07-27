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
    description = serializers.CharField(allow_null=True, required=False)
    status = serializers.CharField()
    project_manager = serializers.CharField(allow_null=True, required=False)
    checklist_actions = ChecklistActionSerializer(many=True)


class JobServiceAssignmentSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    project_manager = BasicUserSerializer(allow_null=True)
    service_name = serializers.CharField(source='service.name')

    class Meta:
        model = JobServiceAssignment
        fields = ['id', 'status', 'project_manager', 'service_name']
        

class JobRetainerServiceAssignmentSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    project_manager = BasicUserSerializer(allow_null=True)
    service_name = serializers.CharField(source='retainer_service.name')

    class Meta:
        model = JobRetainerServiceAssignment
        fields = ['id', 'status', 'project_manager', 'service_name']