from rest_framework import serializers
from ..models import Customer


class CustomerRetainerSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    retainer_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        model = Customer
        fields = ('id', 'name', 'emailAddress', 'logo', 'retainer_amount')