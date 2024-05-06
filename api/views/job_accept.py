from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.models import (Job, JobStatusActivity, UserProfile, JobTag, Tag)

from api.email_notification_service import EmailNotificationService

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

        for job_tag in job.tags.all():
            if job_tag.tag.name == 'Vendor Accepted':
                return

        job_tag = Tag.objects.get(name='Vendor Accepted')

        if not job_tag:
            return Response({'error': 'Tag not found'}, status=status.HTTP_400_BAD_REQUEST)

        JobTag.objects.create(job=job, tag=job_tag)
       
        JobStatusActivity.objects.create(job=job, status='S', activity_type='V', user=request.user)

        full_name = request.user.first_name + ' ' + request.user.last_name

        EmailNotificationService().send_job_accepted_notification(job, full_name)

        return Response(status=status.HTTP_200_OK)
    
    