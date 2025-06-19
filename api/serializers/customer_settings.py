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
            'show_spending_info',
            'retainer_amount',
            'show_job_price',
            'special_instructions',
            'price_list',
            'enable_request_priority',
            'enable_flight_based_scheduled_cleaning'
        )