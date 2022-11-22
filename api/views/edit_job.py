import django
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework.views import APIView
from rest_framework.response import Response
from api.serializers import (JobEditSerializer)
from django.contrib.auth.models import User
from datetime import datetime

from api.notification_util import NotificationUtil

from ..models import (
    Job,
    JobStatusActivity,
    JobCommentCheck
    )


class EditJobView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, id):
        job = get_object_or_404(Job, pk=id)

        if not self.can_edit_job(request.user):
            return Response({'error': 'You do not have permission to edit a job'}, status=status.HTTP_403_FORBIDDEN)
        
        current_status = job.status
        current_price = job.price

        serializer = JobEditSerializer(job, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            
            new_status = serializer.data['status']

            if current_status != new_status:

                if new_status == 'C':
                    job_comment_checks = JobCommentCheck.objects.filter(job=job)

                    if job_comment_checks:
                        job_comment_checks.delete()

                    #Send a notification to all admins and account managers
                    notification_util = NotificationUtil()
                    admins = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True) | Q(groups__name='Account Managers'))

                    for admin in admins:
                        # get the phone number of the admin
                        phone_number = admin.profile.phone_number
                        if phone_number:
                            # send a text message
                            message = f'Job {job.purchase_order} for tail number {job.tailNumber} has been COMPLETED. Please review the job and close it out https://livetakeoff.com/completed/review/{job.id}'
                            notification_util.send(message, phone_number.as_e164)


                    #unassign all services and retainer services
                    for service in job.job_service_assignments.all():
                        service.project_manager = None
                        service.save(update_fields=['project_manager'])

                    for retainer_service in job.job_retainer_service_assignments.all():
                        retainer_service.project_manager = None
                        retainer_service.save(update_fields=['project_manager'])


                    job.completion_date = datetime.now()
                    job.save()


                JobStatusActivity.objects.create(job=job, user=request.user, status=new_status)

            if current_price != serializer.data['price']:
                job.is_auto_priced = False
                job.save()

                JobStatusActivity.objects.create(job=job, user=request.user, status='P', price=serializer.data['price'])

            response = {
                'id': job.id,
            }

            return Response(response, status.HTTP_200_OK)

        return Response({'error': 'Missing Required Fields'}, status.HTTP_400_BAD_REQUEST)



    def can_edit_job(self, user):
        """
        Check if the user has permission to edit a job.
        """
        if user.is_superuser or user.is_staff or user.groups.filter(name='Account Managers').exists():
            return True
        else:
            return False
