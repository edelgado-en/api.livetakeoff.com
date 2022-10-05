from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework .response import Response
from rest_framework.views import APIView
from ..serializers.job import JobSerializer
from ..models import (
        Job,
        JobServiceAssignment,
        JobRetainerServiceAssignment
    )

class JobDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        job = get_object_or_404(Job, pk=id)

        if not self.can_view_job(request, job):
            return Response({'error': 'You do not have permission to view this job'}, status=403)

        serializer = JobSerializer(job)

        return Response(serializer.data)

    # TODO: Move this to a permissions class because you are going to call it from job comments and job photos as well
    def can_view_job(self, request, job):
        if request.user.is_superuser \
          or request.user.is_staff \
          or request.user.groups.filter(name='Account Managers').exists():
           return True

        # You are a Project Manager

        # Get job ids from pending services/retainer_services assigned to the current user
        # If you have at least one pending service assigned to you, you can see the job
        assignments = JobServiceAssignment.objects.filter(project_manager=request.user.id).all()

        for assignment in assignments:
            if assignment.status != 'C' and assignment.job.id == job.id:
                return True
        
        retainer_assignment = JobRetainerServiceAssignment.objects.filter(project_manager=request.user.id).all()

        for assignment in retainer_assignment:
            if assignment.status != 'C' and assignment.job.id == job.id:
                return True

        return False