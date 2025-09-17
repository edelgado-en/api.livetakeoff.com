
from rest_framework import serializers

from ..models import JobFeedbackPhotos

class JobFeedbackPhotosSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = JobFeedbackPhotos
        fields = ['id', 'image']