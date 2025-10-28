from rest_framework import serializers
from ..models import JobCategory
from .basic_user import BasicUserSerializer
from .customer_category import CustomerCategorySerializer

class JobCategorySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    created_by = BasicUserSerializer()
    customer_category = CustomerCategorySerializer()

    class Meta:
        model = JobCategory
        fields = ('id', 'customer_category', 'created_by', 'created_at')