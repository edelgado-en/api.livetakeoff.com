from rest_framework import serializers
from api.models import Vendor

class VendorSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Vendor
        fields = ['id', 'name']