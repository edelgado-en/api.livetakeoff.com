from rest_framework import serializers
from api.models import PriceList
from .basic_user import BasicUserSerializer

class PriceListSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p", read_only=True)
    created_by = BasicUserSerializer(required=False)
    num_customers = serializers.IntegerField(read_only=True)
    num_customer_vendor_mappings = serializers.SerializerMethodField()

    def get_num_customer_vendor_mappings(self, obj):
        # Get the count of unique customers from the VendorCustomerPriceList table associated with this price list
        return obj.vendor_customer_price_lists.values('customer').distinct().count()

    class Meta:
        model = PriceList
        fields = ('id',
                  'name',
                  'description',
                  'created_at',
                  'created_by',
                  'is_vendor',
                  'num_customers',
                  'num_customer_vendor_mappings'
                  )
