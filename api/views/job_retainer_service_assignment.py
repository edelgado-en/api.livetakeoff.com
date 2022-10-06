from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from ..models import JobRetainerServiceAssignment
from ..serializers import JobRetainerServiceAssignmentSerializer

class JobRetainerServiceAssignmentView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, id):
        job_retainer_service_assignment = get_object_or_404(JobRetainerServiceAssignment, pk=id)

        if not self.can_view_assignment(request.user, job_retainer_service_assignment):
            return Response({'error': 'You do not have permission to view this job'}, status=status.HTTP_403_FORBIDDEN)

        serializer = JobRetainerServiceAssignmentSerializer(job_retainer_service_assignment, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def can_view_assignment(self, user, job_retainer_service_assignment):
        if user.is_superuser \
           or user.is_staff \
           or user.groups.filter(name='Account Managers').exists():
           return True
           
        if job_retainer_service_assignment.project_manager.id == user.id:
            return True

        return False