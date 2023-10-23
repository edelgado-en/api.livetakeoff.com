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

        # first get the last 2 jobs where the status is 'C' or 'I' for the tail_number
        # and order by the completion_date field desc
        jobs = Job.objects \
                    .filter(tailNumber=tail_number, status__in=['C', 'I']) \
                    .order_by('-completion_date')[:2]


        # Get ALL the ServiceActivity objects for the provided jobs
        # and order by the timestamp field desc
        qs = ServiceActivity.objects \
                            .filter(job__in=jobs) \
                            .order_by('-timestamp')
        
        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)