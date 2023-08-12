from rest_framework import serializers
from inventory.models import Location

class LocationSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Location
        fields = ('id', 'name', 'description', 'active')