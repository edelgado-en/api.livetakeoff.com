from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from datetime import datetime

import base64

from api.models import (Job, JobStatusActivity)

from api.email_notification_service import EmailNotificationService

class SharedJobReturnView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, encoded_id):
         # Base64 DECODE
        base64_bytes = encoded_id.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        decoded_id = message_bytes.decode('ascii')

        # split message with delimiter - and get the first part
        job_id = int(decoded_id.split('-')[0])

        job = get_object_or_404(Job, pk=job_id)

        # You can only accept a job when the status is Assigned
        if job.status != 'S':
            return Response({'error': 'This job is not in the right status'}, status=status.HTTP_400_BAD_REQUEST)

        full_name = request.data.get('full_name')
        email_address = request.data.get('email')
        phone_number = request.data.get('phone')

        job.returned_full_name = full_name
        job.returned_email = email_address
        job.returned_phone_number = phone_number
        
        job.status = 'A'

        job.save()

        JobStatusActivity.objects.create(job=job, status='A', activity_type='R')

        # update services
        for service in job.job_service_assignments.all():
            service.status = 'U'
            service.project_manager = None
            service.save(update_fields=['status', 'project_manager'])

        for retainer_service in job.job_retainer_service_assignments.all():
            retainer_service.status = 'U'
            retainer_service.project_manager = None
            retainer_service.save(update_fields=['status', 'project_manager'])


        EmailNotificationService().send_job_returned_notification(job, full_name, '')

        return Response(status=status.HTTP_200_OK)