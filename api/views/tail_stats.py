from django.db.models import Q, F
from django.db.models import Count
from rest_framework import (permissions,status)
from rest_framework .response import Response
from rest_framework.generics import ListAPIView

from ..pagination import CustomPageNumberPagination

from ..serializers import TailStatsSerializer

from api.models import (
        Job,
    )


class TailStatsView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination
    serializer_class = TailStatsSerializer

    def get_queryset(self):
        # search by tailNumber
        searchText = self.request.data.get('searchText')
        sortDirection = self.request.data.get('sortDirection')

        # Get a list of tail numbers with its corresponding aircraft types with how many jobs have been associated with them
        # and sort by highest number of jobs first
        qs = Job.objects.values('tailNumber', 'aircraftType__name') \
                        .annotate(job_count=Count('tailNumber')) \
                        .order_by('-job_count') \
                        .distinct('tailNumber') # distinct only works in Postgres


        if searchText:
            qs = qs.filter(tailNumber__icontains=searchText)

        # sort by job count
        if sortDirection == 'asc':
            qs = qs.order_by('job_count')
        else:
            qs = qs.order_by('-job_count')
        

        return qs
    

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
