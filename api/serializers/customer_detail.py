from rest_framework import serializers
from api.models import Customer
from api.serializers import (BasicUserSerializer, CustomerSettingsSerializer)


class CustomerDetailSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    contact = BasicUserSerializer(required=False)
    settings = CustomerSettingsSerializer(required=False)

    class Meta:
        model = Customer
        fields = ('id',
            'name',
            'billingAddress',
            'emailAddress',
            'logo',
            'banner',
            'about',
            'contact',
            'billingInfo',
            'phone_number',
            'settings',
            'active'
        )
