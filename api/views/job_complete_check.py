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

        other_pms_working_on_it = False
        if services_count > 0 or retainer_services_count > 0:
            other_pms_working_on_it = True


        is_admin = False
        if request.user.is_superuser \
                 or request.user.is_staff \
                 or request.user.groups.filter(name='Account Managers').exists():
            is_admin = True


        return Response({
                         'photos_count': photos_count,
                         'other_pms_working_on_it': other_pms_working_on_it,
                         'is_admin': is_admin
                        },
                         status=status.HTTP_200_OK)