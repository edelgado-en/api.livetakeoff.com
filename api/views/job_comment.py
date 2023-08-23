from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from datetime import datetime

from django.contrib.auth.models import User

from ..serializers import (JobCommentSerializer)
from rest_framework.generics import ListCreateAPIView
from ..pagination import CustomPageNumberPagination
from ..models import (JobComments, Job, JobCommentCheck, JobServiceAssignment, JobRetainerServiceAssignment)

from api.notification_util import NotificationUtil

from api.email_util import EmailUtil

class JobCommentView(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobCommentSerializer
    pagination_class = CustomPageNumberPagination
    lookup_url_kwarg = "jobid"

    def get(self, request, *args, **kwargs):
        job_id = self.kwargs.get(self.lookup_url_kwarg)
        job = Job.objects.get(pk=job_id)

        if not self.can_view_comments(self.request.user, job):
            return Response({'error': 'You do not have permission to view comments for this job'}, status=status.HTTP_403_FORBIDDEN)

        return self.list(request, *args, **kwargs)


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

        # if customer user and customer matches job customer then only return public comments
        # request.user.profile.customer and request.user.profile.customer == job.customer
        if self.request.user.profile.customer and self.request.user.profile.customer == job.customer:
            return JobComments.objects.filter(job=job, is_public=True).order_by('created')


        return JobComments.objects.select_related('author').filter(job=job).order_by('created')



    def delete(self, request, *args, **kwargs):
        comment_id = self.kwargs.get(self.lookup_url_kwarg)

        job_comment = get_object_or_404(JobComments, pk=comment_id)
        job_comment.delete()

        return Response(status=status.HTTP_200_OK)



    def patch(self, request, *args, **kwargs):
        comment_id = self.kwargs.get(self.lookup_url_kwarg)

        # toggle is_public field
        job_comment = get_object_or_404(JobComments, pk=comment_id)
        job_comment.is_public = not job_comment.is_public
        job_comment.save()

        return Response(status=status.HTTP_200_OK)



    def create(self, request, *args, **kwargs):
        user = self.request.user
        job_id = self.kwargs.get(self.lookup_url_kwarg)
        job = Job.objects.get(pk=job_id)

        if not self.can_view_comments(user, job):
            return Response({'error': 'You do not have permission to create comment'}, status=status.HTTP_403_FORBIDDEN)


        comment = self.request.data['comment']
        send_sms = self.request.data['sendSMS']
        is_public = self.request.data['isPublic']
        send_email = self.request.data['sendEmail']

        is_customer_user = False

        # when the user is customer and the customer matches the job customer then is_public is always true
        if user.profile.customer and user.profile.customer == job.customer:
            is_public = True
            is_customer_user = True

        job_comment = JobComments(job=job,
                                  comment=comment,
                                  is_public=is_public,
                                  author=user)

        job_comment.save()

        # if is_customer_user True always send sms
        if is_customer_user:
            send_sms = True    


        # if send_sms then send notification to all project managers assigned to this job
        if send_sms:
            notification_util = NotificationUtil()

            # Adding a link is throwing a 30007 error in Twilio
            #message = f'An important message has been added to job {job.purchase_order} for Tail number {job.tailNumber}. Check it out at  http://livetakeoff.com/jobs/{job.id}/comments'

            message = f'An important message has been added to job {job.purchase_order} for Tail number {job.tailNumber}.'

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


            # if a customer user is creating the comment then also send sms to all admins and account managers
            if is_customer_user:
                admins = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True) | Q(groups__name='Account Managers'))
                
                for user in admins:
                    if user.profile.phone_number:
                        if user.profile.phone_number not in unique_phone_numbers:
                            unique_phone_numbers.append(user.profile.phone_number)



            for phone_number in unique_phone_numbers:
                notification_util.send(message, phone_number.as_e164)

        
        if send_email and is_customer_user:
            # get the customer associated with the job
            email_address = job.created_by.email

            if email_address:
                title = f'[{job.tailNumber}] Job Comment Added'
                link = f'http://livetakeoff.com/jobs/{job.id}/comments'

                body = f'''
                <div style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">Job Comment Added</div>
                
                <div>
                    <div style="padding:5px;font-weight: 700;">Tail Number</div>
                    <div style="padding:5px">{job.tailNumber}</div>
                    <div style="padding:5px;font-weight: 700;">Airport</div>
                    <div style="padding:5px">{job.airport.name}</div>
                    <div style="padding:5px;font-weight: 700;">Aircraft</div>
                    <div style="padding:5px">{job.aircraftType.name}</div>
                    <div style="padding:5px;font-weight: 700;">Comment</div>
                    <div style="padding:5px">{comment}</div>
                    <div style="padding:5px;font-weight: 700;">Link</div>
                    <div style="padding:5px">{link}</div>
                </div>
                '''

                email_util = EmailUtil()
                email_util.send_email(email_address, title, body)


        serializer = JobCommentSerializer(job_comment)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def can_view_comments(self, user, job):
        if user.is_superuser \
          or user.is_staff \
          or user.groups.filter(name='Project Managers').exists() \
          or user.groups.filter(name='Internal Coordinators').exists() \
          or user.groups.filter(name='Account Managers').exists():
           return True

        if user.profile.customer and user.profile.customer == job.customer:
            return True

        return False

