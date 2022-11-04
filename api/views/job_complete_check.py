from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from ..models import (
        Job,
        JobServiceAssignment,
        JobRetainerServiceAssignment,
        JobPhotos,
    )


class JobCompleteCheck(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, id):
        job = get_object_or_404(Job, pk=id)

        # Count all the non-customer_uploaded photos associated with this job
        photos_count = JobPhotos.objects.filter(job=job, customer_uploaded=False).count()

        # Count services and retainer services where project_manager does NOT equal the current user
        # and where status is NOT equal to 'C'
        services_count = JobServiceAssignment.objects.filter(
            Q(job=job) &
            ~Q(project_manager=request.user) &
            ~Q(status='C')
        ).count()

        retainer_services_count = JobRetainerServiceAssignment.objects.filter(
            Q(job=job) &
            ~Q(project_manager=request.user) &
            ~Q(status='C')
        ).count()

        assigned_to_other_pms = False

        if services_count > 0 or retainer_services_count > 0:
            assigned_to_other_pms = True


        return Response({
                         'photos_count': photos_count,
                         'assigned_to_other_pms': assigned_to_other_pms
                        },
                         status=status.HTTP_200_OK)