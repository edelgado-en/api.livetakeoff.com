from rest_framework import serializers
from ..models import (
    JobTag
    )

class JobTagSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    tag_name = serializers.CharField(source='tag.name')
    tag_description = serializers.CharField(source='tag.description')
    tag_color = serializers.CharField(source='tag.color')

    class Meta:
        model = JobTag
        fields = ['id', 'tag_name', 'tag_description', 'tag_color']