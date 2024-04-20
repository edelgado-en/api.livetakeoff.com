from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from datetime import datetime

from api.models import (Job, JobStatusActivity, UserProfile, JobTag, Tag)

from api.email_util import EmailUtil

class JobAcceptView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        """ This enpoint is meant to be used by project managers only.
           It allows them to accept a job that has been assigned to them.
            This endpoint is only used if the user is configured to accept jobs.
          """
        job = get_object_or_404(Job, pk=id)

        # You can only accept a job when the status is Assigned
        if job.status != 'S':
            return Response({'error': 'This job is not in the right status'}, status=status.HTTP_400_BAD_REQUEST)

        can_accept_jobs = False
        if request.user.profile:
            can_accept_jobs = request.user.profile.enable_accept_jobs

        if not can_accept_jobs:
            return Response({'error': 'You are not configured to accept jobs'}, status=status.HTTP_403_FORBIDDEN)


        for tag in job.tags.all():
            if tag.name == 'Vendor Accepted':
                return Response({'error': 'This job has already been accepted'}, status=status.HTTP_400_BAD_REQUEST)

        job_tag = Tag.objects.get(name='Vendor Accepted')

        if not job_tag:
            return Response({'error': 'Tag not found'}, status=status.HTTP_400_BAD_REQUEST)


        JobTag.objects.create(job=job, tag=job_tag)
       
        JobStatusActivity.objects.create(job=job, status='S', activity_type='V', user=request.user)

        admins = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True) | Q(groups__name='Account Managers'))

        emails = []

        for user in admins:
            if user.email:
                if user.email not in emails:
                    emails.append(user.email)

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

        subject = f'{job.tailNumber} - Job ACCEPTED by {request.user.first_name} {request.user.last_name}'

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
                        <td style="padding:15px">{job.arrival_formatted_date}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Departure</td>
                        <td style="padding:15px">{job.departure_formatted_date}</td>
                    </tr>
                    <tr>
                        <td style="padding:15px">Complete Before</td>
                        <td style="padding:15px">{job.complete_before_formatted_date}</td>
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