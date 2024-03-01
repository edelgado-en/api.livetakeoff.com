from django.db.models import Q, F
from rest_framework import (permissions,status)
from rest_framework .response import Response
from rest_framework.generics import ListAPIView
from inventory.serializers import (
    LocationItemActivitySerializer,
)

from datetime import (date, datetime, timedelta)

from api.pagination import CustomPageNumberPagination

from inventory.models import (
    LocationItemActivity
)

class LocationItemActivityListView(ListAPIView):
    serializer_class = LocationItemActivitySerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        item_id = self.request.data.get('item_id', None)
        user_id = self.request.data.get('user_id', None)
        item_name = self.request.data.get('item_name', '')
        activity_type = self.request.data.get('activity_type', None)
        dateSelected = self.request.data.get('dateSelected', None)
        location_id = self.request.data.get('location_id', None)

        # get start date and end date based on the dateSelected value provided
        if dateSelected == 'today':
            # start_date should be the beginning of the day and end_date should be now
            today = datetime.now()
            start_date = datetime(today.year, today.month, today.day)
            end_date = datetime.now()

        elif dateSelected == 'yesterday':
            yesterday = datetime.now() - timedelta(days=1)
            start_date = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
            end_date = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
        
        elif dateSelected == 'last7Days':
            today = date.today()
            start_date = today - timedelta(days=7)
            end_date = today

        elif dateSelected == 'lastWeek':
            today = date.today()
            start_date = today - timedelta(days=today.weekday(), weeks=1)
            end_date = start_date + timedelta(days=6)

        elif dateSelected == 'MTD':
            today = date.today()
            start_date = date(today.year, today.month, 1)
            end_date = datetime.now()

        elif dateSelected == 'lastMonth':
            today = date.today()
            first = today.replace(day=1)
            lastMonth = first - timedelta(days=1)
            start_date = lastMonth.replace(day=1)
            
            # check if last month has 31 days or 30 days or 28 days
            if lastMonth.month == 1 or lastMonth.month == 3 \
                or lastMonth.month == 5 or lastMonth.month == 7 or lastMonth.month == 8 \
                or lastMonth.month == 10 or lastMonth.month == 12:
                end_date = lastMonth.replace(day=31)
            
            elif lastMonth.month == 4 or lastMonth.month == 6 or lastMonth.month == 9 or lastMonth.month == 11:
                end_date = lastMonth.replace(day=30)
            
            else:
                end_date = lastMonth.replace(day=28)

        elif dateSelected == 'lastQuarter':
            today = date.today()
            # get today's month and check it is in the first, second, third or fourth quarter. if it is first quarter, then get the previous year's last quarter
            if today.month in [1,2,3]:
                start_date = date(today.year - 1, 10, 1)
                end_date = date(today.year - 1, 12, 31)
            
            elif today.month in [4,5,6]:
                start_date = date(today.year, 1, 1)
                end_date = date(today.year, 3, 31)
            
            elif today.month in [7,8,9]:
                start_date = date(today.year, 4, 1)
                end_date = date(today.year, 6, 30)
            
            elif today.month in [10,11,12]:
                start_date = date(today.year, 7, 1)
                end_date = date(today.year, 9, 30)

        
        elif dateSelected == 'YTD':
            year = datetime.now().year
            start_date = datetime(year, 1, 1)
            end_date = datetime.now()
        
        elif dateSelected == 'lastYear':
            today = date.today()
            start_date = date(today.year - 1, 1, 1)
            end_date = date(today.year - 1, 12, 31)


        qs = LocationItemActivity.objects.all()
        qs = qs.filter(location_item__item__name__icontains=item_name)

        if dateSelected:
            qs = qs.filter(timestamp__range=(start_date, end_date))
                                    
        if item_id:
            qs = qs.filter(location_item__item_id=item_id)

        if user_id:
            qs = qs.filter(user_id=user_id)
        
        if activity_type:
            qs = qs.filter(activity_type=activity_type)

        if location_id:
            qs = qs.filter(location_item__location_id=location_id)

        qs = qs.order_by('-timestamp')

        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)