from django.db.models import Q, F
from django.db.models import Count, Sum
from rest_framework import (permissions,status)
from rest_framework .response import Response
from rest_framework.generics import ListAPIView

from ..pagination import CustomPageNumberPagination

from ..serializers import TailStatsSerializer

from api.models import (
        Job,
        CustomerSettings
    )


class TailStatsView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination
    serializer_class = TailStatsSerializer

    def get_queryset(self):
        # search by tailNumber
        searchText = self.request.data.get('searchText')
        sortSelected = self.request.data.get('sortSelected')


        qs = Job.objects.values('tailNumber', 'aircraftType__name') \
                        .annotate(job_count=Count('tailNumber'))

        # if the current user is a customer and customerSettings.show_spending_info is true OR current user is admin or account manager, then include total_price
        # otherwise, don't include total_price
        if self.request.user.is_superuser \
                 or self.request.user.is_staff \
                 or self.request.user.groups.filter(name='Account Managers').exists() \
                 or (self.request.user.profile.customer and self.request.user.profile.customer.customer_settings.show_spending_info):
            qs = qs.annotate(total_price=Sum('price', filter=Q(status__in=['C', 'I'])))


        # if the current user is a customer, only get the jobs for that customer
        if self.request.user.profile.customer:
            qs = qs.filter(customer=self.request.user.profile.customer)
            qs = qs.exclude(status='T')


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
