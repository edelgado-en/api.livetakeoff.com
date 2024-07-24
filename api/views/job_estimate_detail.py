from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from datetime import datetime

import base64

from api.models import (JobEstimate, JobEstimateDiscount, JobEstimateAdditionalFee)

from api.serializers import (JobEstimateDetailSerializer,)


class JobEstimateDetailView(APIView):
    permission_classes = (permissions.AllowAny,)


    def get(self, request, id):
        estimate = get_object_or_404(JobEstimate, pk=id)

        job_service_estimates = []
        for job_service_estimate in estimate.job_service_estimates.all():
            job_service_estimates.append({
                'id': job_service_estimate.id,
                'name': job_service_estimate.service.name,
                'description': job_service_estimate.service.description,
                'price': job_service_estimate.price,
                'category': job_service_estimate.service.category
            })

        estimate.services = job_service_estimates


        # Base64 ENCODE
        message = str(estimate.id) + '-' + estimate.tailNumber
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        base64_message = base64_bytes.decode('ascii')

        estimate.encoded_id = base64_message

        serializer = JobEstimateDetailSerializer(estimate)

        return Response(serializer.data)
