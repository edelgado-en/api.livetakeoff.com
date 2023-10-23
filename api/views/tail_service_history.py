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

        # Fetch the latest 2 jobs for the tail number that have at least on service activity
        jobs = Job.objects.filter(tailNumber=tail_number, status__in=['C', 'I'],
                                  service_activities__isnull=False) \
                          .order_by('-completion_date')[:2]

        # Get the service activities for the latest 2 jobs
        qs = ServiceActivity.objects.filter(job__in=jobs).order_by('-timestamp')

        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)