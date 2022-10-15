from rest_framework import serializers

from ..models import JobPhotos

class JobPhotoSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    interior = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    size = serializers.ReadOnlyField()
    customer_uploaded = serializers.ReadOnlyField()

    class Meta:
        model = JobPhotos
        fields = ['id', 'created_at', 'name', 'image', 'interior', 'size', 'customer_uploaded']