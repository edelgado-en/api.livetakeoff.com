from rest_framework import serializers
from api.models import RetainerService

class RetainerServiceSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = RetainerService
        fields = ['id', 'name', 'short_name', 'description', 'short_description', 'category']