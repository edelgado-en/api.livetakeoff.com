from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from datetime import datetime

from ..serializers import (JobCommentSerializer)
from rest_framework.generics import ListCreateAPIView
from ..pagination import CustomPageNumberPagination
from ..models import (JobComments, Job, JobCommentCheck, JobServiceAssignment, JobRetainerServiceAssignment)

from api.notification_util import NotificationUtil

class JobCommentView(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobCommentSerializer
    pagination_class = CustomPageNumberPagination
    lookup_url_kwarg = "jobid"

    def get_queryset(self):
        job_id = self.kwargs.get(self.lookup_url_kwarg)
        job = Job.objects.get(pk=job_id)

        now = datetime.now()

        try:
            job_comment_check = JobCommentCheck.objects.get(job=job, user=self.request.user)
            job_comment_check.last_time_check = now
            job_comment_check.save()

        except JobCommentCheck.DoesNotExist:
            job_comment_check = JobCommentCheck(job=job, user=self.request.user, last_time_check=now)
            job_comment_check.save()

        return JobComments.objects.select_related('author').filter(job=job).order_by('created')


    def create(self, request, *args, **kwargs):
        user = self.request.user
        job_id = self.kwargs.get(self.lookup_url_kwarg)
        job = Job.objects.get(pk=job_id)

        comment = self.request.data['comment']
        send_sms = self.request.data['sendSMS']

        job_comment = JobComments(job=job,
                                  comment=comment,
                                  author=user)

        job_comment.save()

        # if send_sms then send notification to all project managers assigned to this job
        if send_sms:
            notification_util = NotificationUtil()
            message = f'An important message has been added to job {job.purchase_order} for Tail number {job.tailNumber}. Check it out at  http://livetakeoff.com/jobs/{job.id}/comments'

            # get all phone numbers for all project managers assigned to this job
            # iterate through jobServiceAssignments and JobRetainerServiceAssignments and get all the unique phone numbers
            unique_phone_numbers = []
            
            job_service_assignments = JobServiceAssignment.objects \
                                                          .select_related('project_manager').filter(job=job)
            
            for assignment in job_service_assignments:
                user = assignment.project_manager
                
                if user and user.profile.phone_number:
                    if user.profile.phone_number not in unique_phone_numbers:
                        unique_phone_numbers.append(user.profile.phone_number)


            job_retainer_service_assignments = JobRetainerServiceAssignment.objects \
                                                            .select_related('project_manager').filter(job=job)
            
            for assignment in job_retainer_service_assignments:
                user = assignment.project_manager
                
                if user and user.profile.phone_number:
                    if user.profile.phone_number not in unique_phone_numbers:
                        unique_phone_numbers.append(user.profile.phone_number)


            for phone_number in unique_phone_numbers:
                notification_util.send(message, phone_number.as_e164)


        serializer = JobCommentSerializer(job_comment)

        return Response(serializer.data, status=status.HTTP_201_CREATED)



