from rest_framework import serializers
from inventory.models import LocationItemActivity
from api.serializers import BasicUserSerializer
from inventory.serializers.location import LocationSerializer
from inventory.serializers.location_item import LocationItemSerializer

class LocationItemActivitySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    user = BasicUserSerializer()
    moved_from = LocationSerializer()
    moved_to = LocationSerializer()
    location_item = LocationItemSerializer()

    class Meta:
        model = LocationItemActivity
        fields = ('id', 'timestamp', 'location_item', 'activity_type',
                  'quantity', 'cost', 'moved_from', 'moved_to', 'user')