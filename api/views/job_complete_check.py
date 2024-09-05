from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from datetime import datetime, timezone

from ..models import (
        Job,
        JobServiceAssignment,
        JobRetainerServiceAssignment,
        JobPhotos,
        JobStatusActivity
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

        is_master_pm = False
        if request.user.profile.master_vendor_pm:
            is_master_pm = True

        # Get the JobStatusActivity for this job where the activity is 'S' and the status is 'W'
        job_status_activity = JobStatusActivity.objects.filter(job=job, activity_type='S', status='W').first()

        start_date = job_status_activity.timestamp

        # Calculate the difference between the start_date and now in seconds
        # Then return and object with hours and minutes
        # use the same timezone
        now = datetime.now(timezone.utc)
        # the start_date needs to be in UTC as well
        start_date = start_date.astimezone(timezone.utc)

        difference = now - start_date

        # breakdown the difference into hours and minutes. Minutes can only go up to 60, if it is higher, it should be an hour
        minutes = difference.seconds / 60
        hours = 0

        if minutes > 60:
            hours = minutes / 60
            minutes = minutes % 60

        # hours should be rounded down to an integer
        hours = int(hours)

        # minutes should be rounded down to an integer
        minutes = int(minutes)

        return Response({
                         'photos_count': photos_count,
                         'other_pms_working_on_it': other_pms_working_on_it,
                         'is_admin': is_admin,
                         'is_master_pm': is_master_pm,
                         'minutes': minutes,
                         'hours': hours
                        },
                         status=status.HTTP_200_OK)