from django.db.models import Q, Sum, F, Func
from django.db.models.functions import ExtractMonth, ExtractWeek
from rest_framework import (permissions, status)

from inventory.serializers import (GeneralStatsSerializer)
from rest_framework.generics import ListAPIView

from inventory.models import (DailyGeneralStats, DailyLocationStats)

from datetime import (date, datetime)

class GeneralStatsListView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = GeneralStatsSerializer

    def get_queryset(self):
        year = self.request.data.get('year', None)
        location_id = self.request.data.get('location_id', None)
        date_grouping = self.request.data.get('date_grouping', None)

        # date_grouping can only be 'Monthly' and 'Weekly'
        # The date_name will change depending on the date_grouping.
        # For monthly, it will be the name of the month, like "August"
        # For weekly, it will be the week number, like "Week 1"
        # All of the other values in the serializer will be summations of the values in the DailyGeneralStats table or DailyLocationStats table depending if location_id is specified

        if location_id:
            # query DailyLocationStats and the result set needs to match GeneralStatsSerializer. The query is a summation of values based on the date_grouping
            # if date_grouping is 'Monthly', then you need to sum all values group by month within the provided year
            # if date_grouping is 'Weekly', then you need to sum all values group by week within the provided year

            # aggregate the values with Sum() and group by the date_name

            if date_grouping == 'Monthly':
                qs = DailyLocationStats.objects \
                                .filter(location_id=location_id, date__year=year) \
                                .annotate(date_name=ExtractMonth('date')) \
                                .values('date_name') \
                                .annotate(total_moving_items=Sum('total_moving_items'),
                                          total_moving_quantity=Sum('total_moving_quantity'),
                                          total_moving_cost=Sum('total_moving_cost'),
                                          total_additions=Sum('total_additions'),
                                          total_add_cost=Sum('total_add_cost'), 
                                          total_subtractions=Sum('total_subtractions'), 
                                          total_expense=Sum('total_expense')) \
                                .order_by('date_name')

            elif date_grouping == 'Weekly':
                qs = DailyLocationStats.objects \
                                .filter(location_id=location_id, date__year=year) \
                                .annotate(date_name=ExtractWeek('date')) \
                                .values('date_name') \
                                .annotate(total_moving_items=Sum('total_moving_items'),
                                          total_moving_quantity=Sum('total_moving_quantity'),
                                          total_moving_cost=Sum('total_moving_cost'),
                                          total_additions=Sum('total_additions'),
                                          total_add_cost=Sum('total_add_cost'), 
                                          total_subtractions=Sum('total_subtractions'), 
                                          total_expense=Sum('total_expense')) \
                                .order_by('date_name')
        
        else:
            if date_grouping == 'Monthly':
                qs = DailyGeneralStats.objects \
                                .filter(date__year=year) \
                                .annotate(date_name=ExtractMonth('date')) \
                                .values('date_name') \
                                .annotate(total_moving_items=Sum('total_moving_items'),
                                          total_moving_quantity=Sum('total_moving_quantity'),
                                          total_moving_cost=Sum('total_moving_cost'),
                                          total_additions=Sum('total_additions'),
                                          total_add_cost=Sum('total_add_cost'), 
                                          total_subtractions=Sum('total_subtractions'), 
                                          total_expense=Sum('total_expense')) \
                                .order_by('date_name')

            elif date_grouping == 'Weekly':
                qs = DailyGeneralStats.objects \
                                .filter(date__year=year) \
                                .annotate(date_name=ExtractWeek('date')) \
                                .values('date_name') \
                                .annotate(total_moving_items=Sum('total_moving_items'),
                                          total_moving_quantity=Sum('total_moving_quantity'),
                                          total_moving_cost=Sum('total_moving_cost'),
                                          total_additions=Sum('total_additions'),
                                          total_add_cost=Sum('total_add_cost'), 
                                          total_subtractions=Sum('total_subtractions'), 
                                          total_expense=Sum('total_expense')) \
                                .order_by('date_name')

        return qs

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)