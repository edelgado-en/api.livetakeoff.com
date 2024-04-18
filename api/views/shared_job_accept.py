from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from datetime import datetime

import base64

from api.models import (Job, JobStatusActivity, Tag, JobTag)

from api.email_util import EmailUtil

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

        admins = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True) | Q(groups__name='Account Managers'))

        emails = []

        for user in admins:
            if user.email:
                if user.email not in emails:
                    emails.append(user.email)

        etd = 'Not Specified'
        if job.estimatedETD:
            etd = job.estimatedETD.strftime('%m/%d/%y %H:%M')

        eta = 'Not Specified'
        if job.estimatedETA:
            eta = job.estimatedETA.strftime('%m/%d/%y %H:%M')
        
        complete_before = 'Not Specified'
        if job.completeBy:
            complete_before = job.completeBy.strftime('%m/%d/%y %H:%M')

        service_names = ''
        for service in job.job_service_assignments.all():
            service_names += service.service.name + ', '

        if service_names:
            service_names = service_names[:-2]

        retainer_service_names = ''
        for retainer in job.job_retainer_service_assignments.all():
            retainer_service_names += retainer.retainer_service.name + ', '
        
        if retainer_service_names:
            retainer_service_names = retainer_service_names[:-2]

        subject = f'{job.tailNumber} - Job ACCEPTED by {full_name}'

        body = f'''
                <div style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">Job Accepted</div>
                <table style="border-collapse: collapse">
                    <tr>
                        <td style="padding:15px">Tail</td>
                        <td style="padding:15px">{job.tailNumber}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Airport</td>
                        <td style="padding:15px">{job.airport.name}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">FBO</td>
                        <td style="padding:15px">{job.fbo.name}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Arrival</td>
                        <td style="padding:15px">{eta}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Departure</td>
                        <td style="padding:15px">{etd}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Complete Before</td>
                        <td style="padding:15px">{complete_before}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Services</td>
                        <td style="padding:15px">{service_names}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Retainer Services</td>
                        <td style="padding:15px">{retainer_service_names}</td>
                    </tr>
                </table>
                <div style="margin-top:20px;padding:5px;font-weight: 700;"></div>
                <a href="http://livetakeoff.com/jobs/{job.id}/details" style="display: inline-block; padding: 0.375rem 0.75rem; margin: 0 5px; font-size: 1rem; font-weight: 400; line-height: 1.5; text-align: center; vertical-align: middle; cursor: pointer; border: 1px solid transparent; border-radius: 0.25rem; transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out; text-decoration: none; color: #212529; background-color: #f8f9fa; border-color: #f8f9fa;">REVIEW</a>
                <div style="margin-top:20px"></div>
                '''

        email_util = EmailUtil()

        body += email_util.getEmailSignature()

        for email in emails:
            email_util.send_email(email, subject, body)


        return Response(status=status.HTTP_200_OK)