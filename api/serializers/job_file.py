from rest_framework import serializers

from ..models import JobFiles

class JobFileSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    size = serializers.ReadOnlyField()
    customer_uploaded = serializers.ReadOnlyField()

    created_at = serializers.DateTimeField(format="%m/%d/%y %H:%M", read_only=True)

    class Meta:
        model = JobFiles
        fields = ['id', 'created_at', 'name', 'file', 'size', 'customer_uploaded', 'is_public']