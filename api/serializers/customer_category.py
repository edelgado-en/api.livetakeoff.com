from rest_framework import serializers
from ..models import (
    CustomerCategory,
    JobCategory
    )

class CustomerCategorySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    jobs_created = serializers.SerializerMethodField()

    def get_jobs_created(self, obj):
        return JobCategory.objects.filter(customer_category=obj).count()

    class Meta:
        model = CustomerCategory
        fields = ['id', 'name', 'is_active', 'jobs_created']