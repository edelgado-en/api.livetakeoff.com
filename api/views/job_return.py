from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User

from ..models import (
        Job,
        JobComments,
        JobStatusActivity
    )

from api.email_notification_service import EmailNotificationService

class JobReturnView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def post(self, request, id):
        job = get_object_or_404(Job, pk=id)

        comment = request.data['comment']

        if not comment:
            return Response({'error': 'Please enter a comment'}, status=status.HTTP_400_BAD_REQUEST)

        # update job
        job.status = 'A'
        job.save()


        # save status activity
        job_status_activity = JobStatusActivity(job=job,
                                                activity_type='R',
                                                status='A',
                                                user=request.user)
        
        job_status_activity.save()


        # update services
        for service in job.job_service_assignments.all():
            service.status = 'U'
            service.project_manager = None
            service.save(update_fields=['status', 'project_manager'])

        for retainer_service in job.job_retainer_service_assignments.all():
            retainer_service.status = 'U'
            retainer_service.project_manager = None
            retainer_service.save(update_fields=['status', 'project_manager'])


        # create comment
        job_comment = JobComments(job=job,
                                  comment=comment,
                                  is_public=False,
                                  author=request.user)

        job_comment.save()

        full_name = request.user.first_name + ' ' + request.user.last_name

        EmailNotificationService().send_job_returned_notification(job, full_name, comment)

        return Response({'success': 'Job returned successfully'}, status=status.HTTP_200_OK)