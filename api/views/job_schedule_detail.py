from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from datetime import datetime

from api.models import (
    JobSchedule,
    JobScheduleService,
    JobScheduleRetainerService
)

from api.serializers import (
    JobScheduleSerializer
)

class JobScheduleDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        job_schedule = get_object_or_404(JobSchedule, pk=id)

        serializer = JobScheduleSerializer(job_schedule)

        return Response(serializer.data)
    
    def patch(self, request, id):
        job_schedule = get_object_or_404(JobSchedule, pk=id)

        is_deleted = request.data.get('is_deleted', None)
        
        if is_deleted is not None:
            job_schedule.is_deleted = is_deleted
            job_schedule.save()

        
        return Response(status=status.HTTP_204_NO_CONTENT)

