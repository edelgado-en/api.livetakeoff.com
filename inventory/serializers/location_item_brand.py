from rest_framework import serializers
from inventory.models import LocationItemBrand

from inventory.serializers.brand import BrandSerializer

class LocationItemBrandSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    brand = BrandSerializer()

    class Meta:
        model = LocationItemBrand
        fields = ('id', 'brand')