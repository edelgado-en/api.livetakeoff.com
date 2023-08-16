from rest_framework import serializers
from inventory.models import ItemProvider

class ItemProviderSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(source='provider.name')

    class Meta:
        model = ItemProvider
        fields = ('id', 'name')