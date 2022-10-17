from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from ..models import (JobServiceAssignment, Job, JobRetainerServiceAssignment)
from django.contrib.auth.models import User
from ..serializers import (
                    JobServiceAssignmentSerializer,
                    JobRetainerServiceAssignmentSerializer,
                    BasicUserSerializer
                )

class JobServiceAssignmentView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        job = get_object_or_404(Job, pk=id)

        assignments = JobServiceAssignment \
                                .objects.select_related('service') \
                                .filter(job=job)

        retainer_assignments = JobRetainerServiceAssignment \
                                    .objects.select_related('retainer_service') \
                                    .filter(job=job)

        # Use a different serializer because you don't need the profile part
        service_assignments = JobServiceAssignmentSerializer(assignments, many=True)
        retainer_service_assignments = JobRetainerServiceAssignmentSerializer(retainer_assignments, many=True)


        # get project managers and their availability
        project_managers = User.objects.filter(groups__name='Project Managers')

        for project_manager in project_managers:
            # We are not doing available soon because I need to have estimated times for all services to properly test
            assignments_in_process = project_manager.job_service_assignments.filter(Q(status='W') | Q(status='A')).count()
            if assignments_in_process > 0:
                project_manager.busy = True
            else:
                project_manager.busy = False

        users = BasicUserSerializer(project_managers, many=True)

        response = {
            'services': service_assignments.data,
            'retainer_services': retainer_service_assignments.data,
            'project_managers': users.data
        }

        return Response(response, status.HTTP_200_OK)



    def patch(self, request, id):
        """ 
        Complete assignment
        """
        job_service_assignment = get_object_or_404(JobServiceAssignment, pk=id)

        if not self.can_view_assignment(request.user, job_service_assignment):
            return Response({'error': 'You do not have permission to view this job'}, status=status.HTTP_403_FORBIDDEN)

        serializer = JobServiceAssignmentSerializer(job_service_assignment, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def can_view_assignment(self, user, job_service_assignment):
        if user.is_superuser \
           or user.is_staff \
           or user.groups.filter(name='Account Managers').exists():
           return True
           
        if job_service_assignment.project_manager.id == user.id:
            return True

        return False


    