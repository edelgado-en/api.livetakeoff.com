from rest_framework import serializers
from api.models import PriceList


class PriceListSerializer(serializers.ModelSerializer):

    class Meta:
        model = PriceList
        fields = ('id', 'name', 'description')
