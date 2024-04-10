from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from datetime import datetime

import base64

from api.models import (Job, JobStatusActivity)

from api.email_util import EmailUtil

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
        email_address = request.data.get('email_address')
        phone_number = request.data.get('phone_number')

        # update job status
        job.status = 'A'
        job.is_publicly_confirmed = True
        job.confirmed_full_name = full_name
        job.confirmed_email_address = email_address
        job.confirmed_phone_number = phone_number
        
        job.save()

        JobStatusActivity.objects.create(job=job, status='A')

        admins = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True) | Q(groups__name='Account Managers'))

        emails = []

        for user in admins:
            if user.email:
                if user.email not in emails:
                    emails.append(user.email)

        subject = f'{job.tailNumber} - Job CONFIRMED by {full_name}'

        body = f'''
                <div style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">Customer Job Request</div>
                <table style="border-collapse: collapse">
                    <tr>
                        <td style="padding:15px">Customer</td>
                        <td style="padding:15px">{job.customer.name}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Job PO</td>
                        <td style="padding:15px">{job.purchase_order}</td>
                    </tr>
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