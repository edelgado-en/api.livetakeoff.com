from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.models import (
        Customer,
        CustomerCategory,
        JobCategory,
        Job
    )

from api.serializers import JobCategorySerializer

class JobCategoryView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        job_id = request.data.get('job_id')
        customer_category_ids = request.data.get('customer_category_ids', [])

        job = get_object_or_404(Job, pk=job_id)

        JobCategory.objects.filter(job=job).delete()

        # Add new job categories
        for category_id in customer_category_ids:
            customer_category = get_object_or_404(CustomerCategory, pk=category_id)
            job_category = JobCategory(
                job=job,
                customer_category=customer_category,
                created_by=request.user
            )
            job_category.save()

        job_categories = JobCategory.objects.filter(job=job)

        serializer = JobCategorySerializer(job_categories, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
        
