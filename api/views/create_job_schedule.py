import json
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.response import Response

from api.models import (
        JobSchedule,
        JobScheduleService,
        JobScheduleRetainerService,
        Service,
        RetainerService
    )

class CreateJobScheduleView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        tailNumber = request.data.get('tailNumber')
        customer_id = request.data.get('customer_id')
        airport_id = request.data.get('airport_id')
        aircraft_type_id = request.data.get('aircraft_type_id')
        fbo_id = request.data.get('fbo_id')
        start_date = request.data.get('start_date', None)
        is_recurrent = request.data.get('is_recurrent', False)
        repeat_every = request.data.get('repeat_every', None)
        comment = request.data.get('comment', None)

        s = request.data.get('services')
        services = []

        if s: 
            services = Service.objects.filter(id__in=s)

        r = request.data.get('retainer_services')
        retainer_services = []

        if r:
            retainer_services = RetainerService.objects.filter(id__in=r)

        # Create JobSchedule
        job_schedule = JobSchedule.objects.create(
            tailNumber=tailNumber,
            customer_id=customer_id,
            airport_id=airport_id,
            aircraftType_id=aircraft_type_id,
            fbo_id=fbo_id,
            start_date=start_date,
            is_recurrent=is_recurrent,
            repeat_every=repeat_every,
            created_by=request.user,
            comment=comment,
        )

        for service in services:
            JobScheduleService.objects.create(
                job_schedule=job_schedule,
                service=service,
            )

        for retainer_service in retainer_services:
            JobScheduleRetainerService.objects.create(
                job_schedule=job_schedule,
                retainer_service=retainer_service,
            )

        return Response({'id': job_schedule.id}, status=status.HTTP_201_CREATED)
