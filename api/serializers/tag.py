from rest_framework import serializers

from api.models import Tag

class TagSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Tag
        fields = ['id', 'name', 'short_name', 'description', 'color']
