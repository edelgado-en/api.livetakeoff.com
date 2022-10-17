from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from ..serializers import (
     JobDetailSerializer,
     )

from ..models import (
        Job,
        JobServiceAssignment,
        JobRetainerServiceAssignment,
        JobPhotos,
        JobStatusActivity,
        JobCommentCheck
    )

class JobDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        job = get_object_or_404(Job, pk=id)

        if not self.can_view_job(request.user, job):
            return Response({'error': 'You do not have permission to view this job'}, status=status.HTTP_403_FORBIDDEN)

        customer_settings = job.customer.customer_settings.all()

        special_instructions = ''

        for customer_setting in customer_settings:
            special_instructions = customer_setting.special_instructions


        job.special_instructions = special_instructions


        job_service_assignments = []
        job_retainer_service_assignments = []

        # Services are shown depending on the user. If you are an account manage/admin, you can see all services
        # if you are a project manager, you can only see the services assigned to you
        if request.user.is_superuser \
            or request.user.is_staff \
            or request.user.groups.filter(name='Account Managers').exists():
                
                # return all services attached to this job
                service_assignments = job.job_service_assignments.select_related('service').all()
                for service_assignment in service_assignments:
                    s_assignment = {
                        'id': service_assignment.id,
                        'name': service_assignment.service.name,
                        'status': service_assignment.status,
                        'checklist_actions': service_assignment.service.checklistActions.all(),
                    }

                    job_service_assignments.append(s_assignment)

                # return all retainer services atached to this job
                retainer_service_assignments = job.job_retainer_service_assignments.select_related('retainer_service').all()
                for retainer_service_assignment in retainer_service_assignments:
                    r_assignment = {
                        'id': retainer_service_assignment.id,
                        'name': retainer_service_assignment.retainer_service.name,
                        'status': retainer_service_assignment.status,
                        'checklist_actions': retainer_service_assignment.retainer_service.checklistActions.all(),
                    }

                    job_retainer_service_assignments.append(r_assignment)

        
        else:
            # return only the services assigned to the current user
            service_assignments = request.user.job_service_assignments.filter(job=job).select_related('service').all()

            for service_assignment in service_assignments:
                s_assignment = {
                    'id': service_assignment.id,
                    'name': service_assignment.service.name,
                    'status': service_assignment.status,
                    'checklist_actions': service_assignment.service.checklistActions.all(),
                }

                job_service_assignments.append(s_assignment)
                

            # retainer services
            retainer_service_assignments = request.user.job_retainer_service_assignments.filter(job=job).select_related('retainer_service').all()

            for retainer_service_assignment in retainer_service_assignments:
                r_assignment = {
                    'id': retainer_service_assignment.id,
                    'name': retainer_service_assignment.retainer_service.name,
                    'status': retainer_service_assignment.status,
                    'checklist_actions': retainer_service_assignment.retainer_service.checklistActions.all(),
                }

                job_retainer_service_assignments.append(r_assignment)

        
        job.service_assignments = job_service_assignments
        job.retainer_service_assignments = job_retainer_service_assignments

        job.total_photos = JobPhotos.objects.filter(job=job).count()

        serializer = JobDetailSerializer(job)

        return Response(serializer.data)


    def patch(self, request, id):
        job = get_object_or_404(Job, pk=id)

        if not self.can_view_job(request.user, job):
            return Response({'error': 'You do not have permission to view this job'}, status=status.HTTP_403_FORBIDDEN)

        serializer = JobDetailSerializer(job, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            # WHEN YOU SET A JOB AS WIP, YOU ALSO HAVE TO SET THE STATUS OF ALL SERVICES ASSIGNMENTS ASSOCIATED TO THIS JOB TO WIP
            # we don't want PMs to have to go to each service and set as WIP, then set as complete. That's too much work and tracking
            # Think about how annoying this will be: Leather Shampo checklist takes you 20 mins, then you have to go to the app
            # click on the job, then click on the service to as as complete. Then click on the other service to set as WIP
            # THIS IS TOO MUCH micromanaging. We want to make it as easy as possible for PMs to do their job.
            if ('status' in request.data 
                    and (request.data['status'] == 'W' or request.data['status'] == 'C')):
                for service in job.job_service_assignments.all():
                    service.status = request.data['status']
                    service.save(update_fields=['status'])

                for retainer_service in job.job_retainer_service_assignments.all():
                    retainer_service.status = request.data['status']
                    retainer_service.save(update_fields=['status'])

                JobStatusActivity.objects.create(job=job, user=request.user, status=request.data['status'])
            
            if 'status' in request.data and request.data['status'] == 'C':
                job_comment_checks = JobCommentCheck.objects.filter(job=job)

                if job_comment_checks:
                    job_comment_checks.delete()

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    # MOVE THIS TO A SERVICE CLASS SO THAT YOU CAN USE IN OTHER VIEWS
    def can_view_job(self, user, job):
        if user.is_superuser \
          or user.is_staff \
          or user.groups.filter(name='Account Managers').exists():
           return True

        # You are a Project Manager
        # Because the PM needs to be able to complete job after completing all the services
        # we allow them if they have at least one service associated with the job

        if job.status == 'I':
            return False
        
        if JobServiceAssignment.objects.filter(project_manager=user.id, job=job).exists() \
            or JobRetainerServiceAssignment.objects.filter(project_manager=user.id, job=job).exists():
            return True

        return False