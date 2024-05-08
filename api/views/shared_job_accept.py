from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

import base64
from api.models import (Job, JobStatusActivity, Tag, JobTag)

from api.email_notification_service import EmailNotificationService

class SharedJobAcceptView(APIView):
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

        for tag in job.tags.all():
            if tag.tag.name == 'Vendor Accepted':
                return Response({'error': 'This job has already been accepted'}, status=status.HTTP_400_BAD_REQUEST)

        job_tag = Tag.objects.get(name='Vendor Accepted')

        if not job_tag:
            return Response({'error': 'Tag not found'}, status=status.HTTP_400_BAD_REQUEST)

        JobTag.objects.create(job=job, tag=job_tag)
       
        JobStatusActivity.objects.create(job=job, status='S', activity_type='V')

        full_name = request.data.get('full_name')
        email_address = request.data.get('email')
        phone_number = request.data.get('phone')

        job.accepted_full_name = full_name
        job.accepted_email = email_address
        job.accepted_phone_number = phone_number
        
        job.save()

        EmailNotificationService().send_job_accepted_notification(job, full_name)

        return Response(status=status.HTTP_200_OK)