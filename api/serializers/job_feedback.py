from rest_framework import serializers

from ..models import JobFeedback

from .basic_user import BasicUserSerializer
from .job_feedback_photos import JobFeedbackPhotosSerializer

class JobFeedbackSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    comment = serializers.ReadOnlyField()
    author = BasicUserSerializer(required=False)
    created = serializers.ReadOnlyField()
    photos = JobFeedbackPhotosSerializer(many=True, read_only=True)

    class Meta:
        model = JobFeedback
        fields = ['id', 'created', 'comment', 'image', 'author', 'photos']