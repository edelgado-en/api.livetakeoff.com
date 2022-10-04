from rest_framework import serializers
from ..models import AircraftType

class AircraftTypeSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = AircraftType
        fields = ('id', 'name')