from rest_framework import serializers
from inventory.models import LocationItem
from inventory.serializers.location import LocationSerializer

from inventory.serializers.basic_item import BasicItemSerializer

class LocationItemDetailSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    location = LocationSerializer()
    item = BasicItemSerializer()

    class Meta:
        model = LocationItem
        fields = ('id', 'location', 'item', 'quantity',
                  'minimum_required', 'threshold',
                  'status')