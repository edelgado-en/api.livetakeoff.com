from rest_framework import serializers
from inventory.models import ItemTag

class ItemTagSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.CharField(source='tag.name')
    
    class Meta:
        model = ItemTag
        fields = ('id', 'name')