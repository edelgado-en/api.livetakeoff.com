from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from datetime import datetime

from django.contrib.auth.models import User

from ..serializers import (JobCommentSerializer)
from rest_framework.generics import ListCreateAPIView
from ..pagination import CustomPageNumberPagination
from ..models import (JobComments, Job, JobCommentCheck, JobServiceAssignment, JobRetainerServiceAssignment, UserEmail)

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
        """
        Admins options:
            send SMS: send text messages to all assigned project managers
            send email: sends emails to all selected emails including the comment and the job information

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
        is_public = self.request.data.get('isPublic', False)
        emails = self.request.data.get('emails', [])

        is_customer_user = False
        is_external_project_manager = False

        # when the user is customer and the customer matches the job customer then is_public is always true
        if user.profile.customer and user.profile.customer == job.customer:
            is_public = True
            is_customer_user = True

        if user.profile.vendor and user.profile.vendor.is_external:
            is_external_project_manager = True

        job_comment = JobComments(job=job,
                                  comment=comment,
                                  is_public=is_public,
                                  author=user)

        job_comment.save()


        # if send_sms then send notification to all project managers assigned to this job
        notification_util = NotificationUtil()
        
        if send_sms:
            message = 'Important note was added to this job'

            message += f'\n• {job.airport.initials}\n• {job.tailNumber}\n• {job.fbo.name}\n'

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

        if send_email:
            title = f'{job.tailNumber} Job Comment Added'

            body = f'''
                    <div style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">Job Comment Added</div>
                    <table style="border-collapse: collapse">
                        <tr>
                            <td style="padding:15px">Comment</td>
                            <td style="padding:15px">{comment}</td>
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
                    <a href="http://livetakeoff.com/jobs/{job.id}/comments" style="display: inline-block; padding: 0.375rem 0.75rem; margin: 0 5px; font-size: 1rem; font-weight: 400; line-height: 1.5; text-align: center; vertical-align: middle; cursor: pointer; border: 1px solid transparent; border-radius: 0.25rem; transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out; text-decoration: none; color: #212529; background-color: #f8f9fa; border-color: #f8f9fa;">REVIEW</a>
                    <div style="margin-top:20px"></div>
                    '''

            email_util = EmailUtil()

            body += email_util.getEmailSignature()

            # iterate through emails and send an email to each email address
            for email_address in emails:
                email_util.send_email(email_address, title, body)

        if is_customer_user or is_external_project_manager:
            # if the customer user is adding a comment, send an email to all admins including the comment and the job information
            admins = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True) | Q(groups__name='Account Managers'))
            emails = []
            for user in admins:
                if user.email:
                    if user.email not in emails:
                        emails.append(user.email)

            subject = ''
            if is_customer_user:
                subject = f'{job.tailNumber} - CUSTOMER ADDED COMMENT'
            elif is_external_project_manager:
                subject = f'{job.tailNumber} - EXTERNAL PROJECT MANAGER ADDED COMMENT'

            body = f'''
                    <div style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">Job Comment Added</div>
                    <table style="border-collapse: collapse">
                        <tr>
                            <td style="padding:15px">Comment</td>
                            <td style="padding:15px">{comment}</td>
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
                    <a href="http://livetakeoff.com/jobs/{job.id}/comments" style="display: inline-block; padding: 0.375rem 0.75rem; margin: 0 5px; font-size: 1rem; font-weight: 400; line-height: 1.5; text-align: center; vertical-align: middle; cursor: pointer; border: 1px solid transparent; border-radius: 0.25rem; transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out; text-decoration: none; color: #212529; background-color: #f8f9fa; border-color: #f8f9fa;">REVIEW</a>
                    <div style="margin-top:20px"></div>
                    '''
            
            email_util = EmailUtil()

            body += email_util.getEmailSignature()

            for email in emails:
                email_util.send_email(email, subject, body)


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

