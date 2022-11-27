from django.db.models import Q, F
from django.db.models import Count, Sum
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
        sortSelected = self.request.data.get('sortSelected')

        # Get the list of tail numbers with aircraftType names the count of total jobs and the total price of those jobs but only for jobs with status C or I
        # and sort by highest number of jobs first

        qs = Job.objects.values('tailNumber', 'aircraftType__name') \
                        .annotate(job_count=Count('tailNumber'), total_price=Sum('price', filter=Q(status__in=['C', 'I'])))

        if searchText:
            qs = qs.filter(tailNumber__icontains=searchText)

        
        if sortSelected == 'total_price_desc':
            qs = qs.order_by('-total_price')

        elif sortSelected == 'total_price_asc':
            qs = qs.order_by('total_price')

        elif sortSelected == 'job_count_desc':
            qs = qs.order_by('-job_count')
        
        elif sortSelected == 'job_count_asc':
            qs = qs.order_by('job_count')

        return qs
    

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
