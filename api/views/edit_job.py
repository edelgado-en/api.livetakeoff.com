import django
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework.views import APIView
from rest_framework.response import Response
from api.serializers import (JobSerializer, JobEditSerializer)

from ..models import (
    Job,
    Service,
    RetainerService,
    AircraftType,
    Airport,
    Customer,
    FBO,
    JobServiceAssignment,
    JobRetainerServiceAssignment
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

        print(serializer.validated_data['services'])
        print(serializer.validated_data['retainerServices'])
        services = serializer.validated_data['services']
        retainer_services = serializer.validated_data['retainerServices']

        # TODO: you have to get the existing services to delete the ones that are not included


        # TODO: you have to handle unassign services, you have to compare the existing services with
        # the newly provided list of services and delete the ones not included

        #for service in services:
            #assignment = JobServiceAssignment(job=job,service=service)
           # assignment.save()

        #for retainer_service in retainer_services:
         #   assignment = JobRetainerServiceAssignment(job=job, retainer_service=retainer_service)
          #  assignment.save()


        # TODO: Calculate estimated completion time based on the estimated times of the selected services and aircraft type

        response = {
            'id': job.id,
            'tailNumber': job.tailNumber
        }

        return Response(response, status.HTTP_200_OK)



    def can_edit_job(self, user):
        """
        Check if the user has permission to edit a job.
        """
        if user.is_superuser or user.is_staff or user.groups.filter(name='Account Managers').exists():
            return True
        else:
            return False
