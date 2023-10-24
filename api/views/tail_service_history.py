from django.db.models import Q, F
from rest_framework import (permissions,status)
from rest_framework .response import Response
from rest_framework.generics import ListAPIView
from datetime import (date, datetime, timedelta)

from api.serializers import (
        ServiceActivitySerializer,
    )

from ..pagination import CustomPageNumberPagination
from api.models import (
        ServiceActivity,
        UserProfile,
        Job
    )

class TailServiceHistoryListView(ListAPIView):
    serializer_class = ServiceActivitySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        tail_number = self.request.data.get('tail_number', None)

        jobs = Job.objects.filter(tailNumber=tail_number, status__in=['C', 'I']).order_by('-completion_date')[:10]

        jobs_with_service_activities = []

        for job in jobs:
            if ServiceActivity.objects.filter(job=job).exists():
                jobs_with_service_activities.append(job)

        qs = ServiceActivity.objects.filter(job__in=jobs_with_service_activities).order_by('-timestamp')

        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)