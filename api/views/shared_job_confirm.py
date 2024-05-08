from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User

import base64

from api.models import (Job, JobStatusActivity)

from api.email_notification_service import EmailNotificationService

class SharedJobConfirmView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, encoded_id):
         # Base64 DECODE
        base64_bytes = encoded_id.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        decoded_id = message_bytes.decode('ascii')

        # split message with delimiter - and get the first part
        job_id = int(decoded_id.split('-')[0])

        job = get_object_or_404(Job, pk=job_id)

        # if this job has been confirmed already, throw an error
        if job.status != 'U':
            return Response({'error': 'This job is not in the right status'}, status=status.HTTP_400_BAD_REQUEST)

        # if this job has been confirmed already, throw an error
        if job.is_publicly_confirmed:
            return Response({'error': 'This job has already been confirmed'}, status=status.HTTP_400_BAD_REQUEST)

        full_name = request.data.get('full_name')
        email_address = request.data.get('email')
        phone_number = request.data.get('phone')

        # update job status
        job.status = 'A'
        job.is_publicly_confirmed = True
        job.confirmed_full_name = full_name
        job.confirmed_email = email_address
        job.confirmed_phone_number = phone_number
        
        job.save()

        JobStatusActivity.objects.create(job=job, status='A')

        EmailNotificationService().send_job_confirmed_notification(job, full_name)

        return Response(status=status.HTTP_200_OK)