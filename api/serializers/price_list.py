from rest_framework import serializers
from api.models import PriceList
from .basic_user import BasicUserSerializer

class PriceListSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%m/%d/%Y %I:%M %p", read_only=True)
    created_by = BasicUserSerializer(required=False)
    num_customers = serializers.IntegerField(read_only=True)

    class Meta:
        model = PriceList
        fields = ('id', 'name', 'description', 'created_at', 'created_by', 'num_customers')
