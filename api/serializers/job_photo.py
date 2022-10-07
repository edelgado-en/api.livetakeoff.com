from rest_framework import serializers

from ..models import JobPhotos

class JobPhotoSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobPhotos
        fields = ['id', 'created_at', 'name', 'image', 'interior']