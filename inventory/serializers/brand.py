from rest_framework import serializers
from inventory.models import Brand

class BrandSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Brand
        fields = ('id', 'name')