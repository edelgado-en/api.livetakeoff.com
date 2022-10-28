from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User

from api.models import (
        JobRetainerServiceAssignment,
        Job,
        RetainerService
    )

from api.serializers import JobRetainerServiceAssignmentSerializer

class JobRetainerServiceAssignmentView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, id):
        """ 
        Completes assignment
        """
        job_retainer_service_assignment = get_object_or_404(JobRetainerServiceAssignment, pk=id)

        if not self.can_view_assignment(request.user, job_retainer_service_assignment):
            return Response({'error': 'You do not have permission to view this job'}, status=status.HTTP_403_FORBIDDEN)

        serializer = JobRetainerServiceAssignmentSerializer(job_retainer_service_assignment, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def post(self, request, id):
        job = get_object_or_404(Job, pk=id)
        retainer_service = get_object_or_404(RetainerService, pk=request.data['retainer_service_id'])

        project_manager = request.data['user_id']

        # TODO: add validation to ensure the service to be added does not already exist for this job

        # TODO: if all services are assigned, then the job status should be assigned if it less than assigned

        if project_manager is not None:
            project_manager = get_object_or_404(User, pk=request.data['user_id'])
            status = 'A'
        else:
            status = 'U'

        retainer_assignment = JobRetainerServiceAssignment(job=job,
                                                           project_manager=project_manager,
                                                           retainer_service=retainer_service,
                                                           status=status)
        retainer_assignment.save()

        serializer = JobRetainerServiceAssignmentSerializer(retainer_assignment)

        return Response(serializer.data)   

    
    def delete(self, request, id):
        job_retainer_service_assignment = get_object_or_404(JobRetainerServiceAssignment, pk=id)

        job_retainer_service_assignment.delete()

        return Response({'message': 'Delete successfully'}, status.HTTP_200_OK)



    def can_view_assignment(self, user, job_retainer_service_assignment):
        if user.is_superuser \
           or user.is_staff \
           or user.groups.filter(name='Account Managers').exists():
           return True
           
        if job_retainer_service_assignment.project_manager.id == user.id:
            return True

        return False