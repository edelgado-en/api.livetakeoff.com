from rest_framework import serializers
from inventory.models import Item

class LightItemSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Item
        fields = ('id', 'name')