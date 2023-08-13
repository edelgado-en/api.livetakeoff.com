from rest_framework import serializers
from inventory.models import LocationItem
from inventory.serializers.location import LocationSerializer

class LocationItemSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    location = LocationSerializer()

    class Meta:
        model = LocationItem
        fields = ('id', 'location', 'quantity', 'minimum_required', 'threshold', 'status')