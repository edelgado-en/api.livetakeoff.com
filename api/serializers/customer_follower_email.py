from rest_framework import serializers
from ..models import CustomerFollowerEmail

class CustomerFollowerEmailSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = CustomerFollowerEmail
        fields = ('id', 'email', 'customer')