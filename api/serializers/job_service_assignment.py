from rest_framework import serializers
from ..models import (JobServiceAssignment, JobRetainerServiceAssignment)

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

    class Meta:
        model = JobServiceAssignment
        fields = ['id', 'status']

class JobRetainerServiceAssignmentSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = JobRetainerServiceAssignment
        fields = ['id', 'status']