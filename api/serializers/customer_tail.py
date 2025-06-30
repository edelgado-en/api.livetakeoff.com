from rest_framework import serializers
from ..models import CustomerTail

class CustomerTailSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    customer_name = serializers.SerializerMethodField()
    last_interior_level_1_service_date = serializers.DateTimeField(format="%m/%d/%y", read_only=True)
    last_interior_level_2_service_date = serializers.DateTimeField(format="%m/%d/%y", read_only=True)
    last_exterior_level_1_service_date = serializers.DateTimeField(format="%m/%d/%y", read_only=True)
    last_exterior_level_2_service_date = serializers.DateTimeField(format="%m/%d/%y", read_only=True)


    def get_customer_name(self, obj):
        return obj.customer.name if obj.customer else None

    class Meta:
        model = CustomerTail
        fields = ('id',
                    'tail_number',
                    'aircraft_type_name',
                    'status',
                    'customer_name',
                    'is_active',
                    'is_interior_level_1_service_due',
                    'is_interior_level_2_service_due',
                    'is_exterior_level_1_service_due',
                    'is_exterior_level_2_service_due',
                    'flights_since_last_interior_level_1_service',
                    'flights_since_last_interior_level_2_service',
                    'flights_since_last_exterior_level_1_service',
                    'flights_since_last_exterior_level_2_service',
                    'last_interior_level_1_service_date',
                    'last_interior_level_2_service_date',
                    'last_exterior_level_1_service_date',
                    'last_exterior_level_2_service_date',
                    'last_interior_level_1_location',
                    'last_interior_level_2_location',
                    'last_exterior_level_1_location',
                    'last_exterior_level_2_location',
                  )