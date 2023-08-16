from rest_framework import serializers
from inventory.models import LocationItem
from inventory.serializers.location import LocationSerializer

from inventory.serializers.location_item_brand import LocationItemBrandSerializer

class LocationItemSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    location = LocationSerializer()
    location_item_brands = LocationItemBrandSerializer(many=True, read_only=True)

    class Meta:
        model = LocationItem
        fields = ('id', 'location', 'quantity',
                  'minimum_required', 'threshold',
                  'status', 'location_item_brands')