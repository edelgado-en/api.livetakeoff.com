from rest_framework import serializers
from ..models import Airport

class AirportSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Airport
        fields = ('id', 'name')