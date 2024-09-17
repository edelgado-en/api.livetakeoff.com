from rest_framework import serializers
from api.models import Vendor

class VendorSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = Vendor
        fields = ['id',
                  'name',
                  'billing_address',
                  'emails',
                  'phone_numbers',
                  'logo',
                  'is_external',
                  'active']