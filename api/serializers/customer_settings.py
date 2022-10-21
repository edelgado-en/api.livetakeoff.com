from rest_framework import serializers
from api.models import CustomerSettings
from api.serializers import PriceListSerializer


class CustomerSettingsSerializer(serializers.ModelSerializer):
    price_list = PriceListSerializer(required=False)

    class Meta:
        model = CustomerSettings
        fields = (
            'id',
            'allow_cancel_job',
            'retainer_amount',
            'show_job_price',
            'special_instructions',
            'price_list'
        )