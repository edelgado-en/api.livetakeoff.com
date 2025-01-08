from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User

from api.models import (Job, UserEmail, JobFollowerEmail)

class UserJobEmailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, job_id):
        job = Job.objects.get(pk=job_id)

        user = job.created_by

        unique_emails = []

        job_follower_emails = JobFollowerEmail.objects.filter(job=job).all()

        follower_emails = []

        for job_follower_email in job_follower_emails:
            if job_follower_email.email not in [email['email'] for email in follower_emails]:
                follower_emails.append({'id': job_follower_email.id, 'email': job_follower_email.email})

        email = user.email

        if email:
            unique_emails.append({'id': user.id, 'email': email})

        user_emails = UserEmail.objects.filter(user=user).all()

        for user_email in user_emails:
            if user_email.email not in [email['email'] for email in unique_emails]:
                unique_emails.append({'id': user_email.id, 'email': user_email.email})

        ##########################################

        unique_project_manager_emails = []

        for job_service_assignment in job.job_service_assignments.all():
            project_manager = job_service_assignment.project_manager

            if project_manager:
                if project_manager.email not in [email['email'] for email in unique_project_manager_emails]:
                    unique_project_manager_emails.append({'id': project_manager.id, 'email': project_manager.email})
                
                project_manager_emails = UserEmail.objects.filter(user=project_manager).all()

                for project_manager_email in project_manager_emails:
                    if project_manager_email.email not in [email['email'] for email in unique_project_manager_emails]:
                        unique_project_manager_emails.append({'id': project_manager_email.id, 'email': project_manager_email.email})

        for job_retainer_service_assignment in job.job_retainer_service_assignments.all():
            project_manager = job_retainer_service_assignment.project_manager

            if project_manager:
                if project_manager.email not in [email['email'] for email in unique_project_manager_emails]:
                    unique_project_manager_emails.append({'id': project_manager.id, 'email': project_manager.email})

                project_manager_emails = UserEmail.objects.filter(user=project_manager).all()

                for project_manager_email in project_manager_emails:
                    if project_manager_email.email not in [email['email'] for email in unique_project_manager_emails]:
                        unique_project_manager_emails.append({'id': project_manager_email.id, 'email': project_manager_email.email})

        return Response({'emails': unique_emails,
                         'project_manager_emails': unique_project_manager_emails,
                         'follower_emails': follower_emails
                         }, status=status.HTTP_200_OK)





    


    
    





