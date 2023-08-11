from rest_framework import serializers
from inventory.models import Item

class ItemSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Item
        fields = ('id', 'name', 'description', 'area', 'measure_by', 'cost_per_unit', 'photo')