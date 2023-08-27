from rest_framework import serializers
from inventory.models import Item
from inventory.serializers.location_item import LocationItemSerializer
from inventory.serializers.item_tag import ItemTagSerializer
from inventory.serializers.item_provider import ItemProviderSerializer

class ItemDetailSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    location_items = serializers.SerializerMethodField()
    tags = ItemTagSerializer(many=True, read_only=True)
    providers = ItemProviderSerializer(many=True, read_only=True)

    def get_location_items(self, obj):
        location_items = obj.location_items.all().order_by('location__name')
        serializer = LocationItemSerializer(location_items, many=True)
        return serializer.data

    class Meta:
        model = Item
        fields = ('id', 'name', 'description', 'area',
                  'measure_by', 'cost_per_unit', 'photo',
                  'location_items', 'tags', 'providers',
                  'created_by', 'active')