from django.db.models import Q, F
from django.db import models
from django.db.models import Count, Sum, Func
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from datetime import (date, datetime, timedelta)

from api.models import (
    RetainerServiceActivity,
    UserProfile,
)

class RetainerServiceReportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        user_profile = UserProfile.objects.get(user=request.user)
        is_customer = user_profile and user_profile.customer is not None

        if not self.can_view_dashboard(request.user, is_customer):
            return Response({'error': 'You do not have permission to view this page'}, status=status.HTTP_403_FORBIDDEN)

        service_id = self.request.data.get('service_id', None)
        airport_id = self.request.data.get('airport_id', None)
        fbo_id = self.request.data.get('fbo_id', None)
        tail_number = self.request.data.get('tail_number', None)
        customer_id = self.request.data.get('customer_id', None)

        dateSelected = request.data.get('dateSelected')

        

        # get start date and end date based on the dateSelected value provided
        if dateSelected == 'yesterday':
            yesterday = datetime.now() - timedelta(days=1)
            start_date = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
            end_date = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
        
        elif dateSelected == 'last7Days':
            today = date.today()
            start_date = today - timedelta(days=7)
            end_date = datetime.now()

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

        qs = RetainerServiceActivity.objects.filter(status='C',
                                            timestamp__gte=start_date, timestamp__lte=end_date)
        
        if service_id:
            qs = qs.filter(retainer_service_id=service_id)
        
        if airport_id:
            qs = qs.filter(job__airport_id=airport_id)

        if fbo_id:
            qs = qs.filter(job__fbo_id=fbo_id)

        if tail_number:
            qs = qs.filter(job__tailNumber__icontains=tail_number)

        if is_customer:
            qs = qs.filter(job__customer_id=user_profile.customer.id)

        if customer_id:
            qs = qs.filter(job__customer_id=customer_id)

        # number of services
        number_of_services_completed = qs.count()

        # number of unique tailNumbers
        number_of_unique_tail_numbers = qs.values('job__tailNumber').distinct().count()

        # Number of unique locations
        number_of_unique_locations = qs.values('job__airport__name').distinct().count()

        return Response({
            'number_of_services_completed': number_of_services_completed,
            'number_of_unique_tail_numbers': number_of_unique_tail_numbers,
            'number_of_unique_locations': number_of_unique_locations,
            }
            , status=status.HTTP_200_OK)
    
    def can_view_dashboard(self, user, is_customer):
        if user.is_superuser or user.is_staff or is_customer:
            return True
        
        return False
                                