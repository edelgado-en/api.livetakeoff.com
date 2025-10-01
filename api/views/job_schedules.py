from django.db.models import Q, F
from rest_framework import (permissions,status)
from rest_framework .response import Response
from rest_framework.generics import ListAPIView
from ..serializers import (
        JobScheduleSerializer,
    )

from pathlib import Path
import json

from django.contrib.auth.models import User

from ..pagination import CustomPageNumberPagination
from ..models import (
        JobSchedule,
        UserProfile
    )

class JobScheduleListView(ListAPIView):
    serializer_class = JobScheduleSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        tailNumber = self.request.data.get('tailNumber', None)

        qs = JobSchedule.objects.filter(is_deleted=False).order_by('-created_at')

        if tailNumber:
            qs = qs.filter(tailNumber__icontains=tailNumber)

        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)