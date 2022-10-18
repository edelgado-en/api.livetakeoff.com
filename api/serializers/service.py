from rest_framework import serializers
from ..models import Service

class ServiceSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Service
        fields = ['id', 'name', 'description']