from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from datetime import datetime

import base64

from api.models import (JobEstimate)

from api.serializers import (JobEstimateDetailSerializer,)

from api.sms_notification_service import SMSNotificationService

class SharedJobEstimateDetailView(APIView):
    permission_classes = (permissions.AllowAny,)


    def get(self, request, encoded_id):
        # Base64 DECODE
        base64_bytes = encoded_id.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode('ascii')

        # split message with delimiter - and get the first part
        estimate_id = int(message.split('-')[0])

        estimate = get_object_or_404(JobEstimate, pk=estimate_id)

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
        encoded_id = base64_bytes.decode('ascii')

        estimate.encoded_id = encoded_id

        serializer = JobEstimateDetailSerializer(estimate)

        return Response(serializer.data)


    def post(self, request, encoded_id):
         # Base64 DECODE
        base64_bytes = encoded_id.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        decoded_id = message_bytes.decode('ascii')

        # split message with delimiter - and get the first part
        estimate_id = int(decoded_id.split('-')[0])

        estimate = get_object_or_404(JobEstimate, pk=estimate_id)

        # if this estimate has been processed already, throw an error
        if estimate.is_processed:
            return Response({'error': 'This estimate has already been processed'}, status=status.HTTP_400_BAD_REQUEST)

        full_name = request.data.get('full_name')
        email = request.data.get('email')
        phone = request.data.get('phone')

        # update estimate status
        estimate.status = request.data.get('status')
        estimate.accepted_full_name = full_name
        estimate.accepted_email = email
        estimate.accepted_phone_number = phone
        estimate.is_processed = True
        estimate.processed_at = datetime.now()
        
        estimate.save()

        SMSNotificationService().send_job_estimate_notification(estimate)


        return Response(status=status.HTTP_200_OK)