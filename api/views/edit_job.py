import django
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework.views import APIView
from rest_framework.response import Response
from api.serializers import (JobEditSerializer)

from ..models import (
    Job
    )


class EditJobView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, id):
        job = get_object_or_404(Job, pk=id)

        if not self.can_edit_job(request.user):
            return Response({'error': 'You do not have permission to edit a job'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = JobEditSerializer(job, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            
            response = {
                'id': job.id,
            }

            return Response(response, status.HTTP_200_OK)

        return Response({'error': 'Missing Required Fields'}, status.HTTP_400_BAD_REQUEST)



    def can_edit_job(self, user):
        """
        Check if the user has permission to edit a job.
        """
        if user.is_superuser or user.is_staff or user.groups.filter(name='Account Managers').exists():
            return True
        else:
            return False
