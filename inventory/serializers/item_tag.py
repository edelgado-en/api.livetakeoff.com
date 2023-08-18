from rest_framework import serializers
from inventory.models import ItemTag

class ItemTagSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    tag_id = serializers.IntegerField(source='tag.id')
    name = serializers.CharField(source='tag.name')
    
    class Meta:
        model = ItemTag
        fields = ('id', 'tag_id', 'name')