from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from datetime import datetime

from ..serializers import (JobCommentSerializer)
from rest_framework.generics import ListCreateAPIView
from ..pagination import CustomPageNumberPagination
from ..models import (JobComments, Job, JobCommentCheck, UserCustomer)

from api.sms_notification_service import SMSNotificationService
from api.email_notification_service import EmailNotificationService

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

        if self.request.user.profile.customer:
            if self.request.user.profile.customer == job.customer:
                return JobComments.objects.filter(job=job, is_public=True).order_by('created')

            # Get extra customers from UserCustomer for this user
            user_customers = UserCustomer.objects.filter(user=self.request.user).all()
            for user_customer in user_customers:
                if user_customer.customer == job.customer:
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
        """
        Admins options:
            send SMS: send text messages to all assigned project managers
            send email: sends emails to all selected emails including the comment and the job information
            send email to project managers: sends emails to all assigned project managers including the comment and the job information

        Additional functionality:
            1) When customer user adds a comment, an automatic email is send to all admins containing the comment and the job information
            2) When an external project manager adds a comment, an automatic email is send to all admins
        """
        user = self.request.user
        job_id = self.kwargs.get(self.lookup_url_kwarg)
        job = Job.objects.get(pk=job_id)

        if not self.can_view_comments(user, job):
            return Response({'error': 'You do not have permission to create comment'}, status=status.HTTP_403_FORBIDDEN)


        comment = self.request.data['comment']
        send_sms = self.request.data.get('sendSMS', False)
        send_email = self.request.data.get('sendEmail', False)
        send_email_to_project_manager = self.request.data.get('sendEmailToProjectManager', False)
        send_email_to_followers = self.request.data.get('sendEmailToFollowers', False)
        is_public = self.request.data.get('isPublic', False)
        emails = self.request.data.get('emails', [])
        projectManagerEmails = self.request.data.get('projectManagerEmails', [])
        followerEmails = self.request.data.get('followerEmails', [])

        is_customer_user = False
        is_external_project_manager = False

        if user.profile.customer:
            if user.profile.customer == job.customer:
                is_customer_user = True
                is_public = True

            # Get extra customers from UserCustomer for this user
            user_customers = UserCustomer.objects.filter(user=user).all()
            for user_customer in user_customers:
                if user_customer.customer == job.customer:
                    is_customer_user = True
                    is_public = True

        if user.profile.vendor and user.profile.vendor.is_external:
            is_external_project_manager = True

        job_comment = JobComments(job=job,
                                  comment=comment,
                                  is_public=is_public,
                                  author=user)

        job_comment.save()

        if send_sms:
            SMSNotificationService().send_job_comment_added_notification(job)


        if send_email:
            EmailNotificationService().send_job_comment_added_notification(job, comment, emails)

        if send_email_to_project_manager:
            EmailNotificationService().send_job_comment_added_notification(job, comment, projectManagerEmails)

        if send_email_to_followers:
            EmailNotificationService().send_job_comment_added_notification(job, comment, followerEmails)


        if is_customer_user or is_external_project_manager:
            EmailNotificationService().send_job_comment_added_notification_to_admins(job, comment,
                                                                                     is_customer_user,
                                                                                     is_external_project_manager)

        serializer = JobCommentSerializer(job_comment)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def can_view_comments(self, user, job):
        if user.is_superuser \
          or user.is_staff \
          or user.groups.filter(name='Project Managers').exists() \
          or user.groups.filter(name='Internal Coordinators').exists() \
          or user.groups.filter(name='Account Managers').exists():
           return True

        if user.profile.customer:
            if user.profile.customer == job.customer:
                return True

            # Get extra customers from UserCustomer for this user
            user_customers = UserCustomer.objects.filter(user=user).all()
            for user_customer in user_customers:
                if user_customer.customer == job.customer:
                    return True

        return False

