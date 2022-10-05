from rest_framework import serializers

class ChecklistActionSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()


class JobServiceAssignmentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    status = serializers.CharField()
    checklist_actions = ChecklistActionSerializer(many=True)