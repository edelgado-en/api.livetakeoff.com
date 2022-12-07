from django.db.models import Q, F
from django.db import models
from django.db.models import Count, Sum, Func
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from datetime import (date, datetime, timedelta)
import pytz
from email.utils import parsedate_tz, mktime_tz

from api.models import (
    ServiceActivity,
    RetainerServiceActivity,
    Job,
    JobStatusActivity,
    UserProfile,
    PriceListEntries
)

class TeamProductivityView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        dateSelected = request.data.get('dateSelected')

        # get start date and end date based on the dateSelected value provided
        if dateSelected == 'yesterday':
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
            if lastMonth.month == 1 or lastMonth.month == 3 or lastMonth.month == 5 or lastMonth.month == 7 or lastMonth.month == 8 or lastMonth.month == 10 or lastMonth.month == 12:
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


        # Get the total number of jobs with status I in the last 30 days by querying at the jobStatusActivity table
        qs = JobStatusActivity.objects.filter(
            Q(status__in=['I']) &
            Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        ).values('job__id').annotate(
            total=Count('job__id')
        ).values('total')

        total_jobs = 0
        for item in qs:
            total_jobs += item['total']
        
        
        # Get the total number of services with statuc C in the last 30 days by querying at the serviceActivity table
        qs = ServiceActivity.objects.filter(
            Q(status='C') &
            Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        ).values('service__name').annotate(
            total=Count('service__id')
        ).values('service__name', 'total')

        grand_total_services = 0
        for item in qs:
            grand_total_services += item['total']

        
        # Get the total number of retainer services with status C in the last 30 days by querying at the retainerServiceActivity table
        qs = RetainerServiceActivity.objects.filter(
            Q(status='C') &
            Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        ).values('retainer_service__name').annotate(
            total=Count('retainer_service__id')
        ).values('retainer_service__name', 'total')

        grand_total_retainer_services = 0
        for item in qs:
            grand_total_retainer_services += item['total']

        
        # Get the total revenue for the last 30 days. This is the sum of the job price for all distinct job ids in jobStatusActivity table where the status is I
        # first, get the list of DISTINCT job ids from the jobStatusActivity table where the status is I
        qs = JobStatusActivity.objects.filter(
            Q(status__in=['I']) &
            Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        ).values('job__id').distinct()

        # then, get the sum of the job price for all the jobs in the list
        total_jobs_revenue = 0
        for item in qs:
            job = Job.objects.get(id=item['job__id'])
            if job.price is not None:
                total_jobs_revenue += job.price


        # Get the top 5 services in the last 30 days by querying the ServiceActivity table and join to Services Table to get the service name. The resulset should be service name with its corresponding times the service was completed in the last 30 days
        qs = ServiceActivity.objects.filter(
            Q(status='C') &
            Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        ).values('service__name').annotate(
            total=Count('service__id')
        ).values('service__name', 'total').order_by('-total')[:5]

        top_services = []
        # add a percentage value to each service which is calculated based on the top 5 services provided
        for item in qs:
            top_services.append({
                'name': item['service__name'],
                'total': item['total'],
                'percentage': round((item['total'] / grand_total_services) * 100, 2)
            })

        
        # Get the top 5 retainer services in the last 30 days by querying the RetainerServiceActivity table and join to RetainerServices Table to get the retainer service name. The resulset should be retainer service name with its corresponding times the retainer service was completed in the last 30 days
        qs = RetainerServiceActivity.objects.filter(
            Q(status='C') &
            Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        ).values('retainer_service__name').annotate(
            total=Count('retainer_service__id')
        ).values('retainer_service__name', 'total').order_by('-total')[:5]

        top_retainer_services = []
        # add a percentage value to each retainer service which is calculated based on the top 5 retainer services provided
        for item in qs:
            top_retainer_services.append({
                'name': item['retainer_service__name'],
                'total': item['total'],
                'percentage': round((item['total'] / grand_total_retainer_services) * 100, 2)
            })


        # get the list of all users that completed services in the last 30 days. The resultSet should be the user first name, last name and avatar (by querying the userProfile table) with the total number of services and retainer services completed, and the total revenue generated by the user in the last 30 days. The revenue generated by each user is calculated based on service, aircraft type, and price list of the customer associated with the job for which the service was completed. The price is calculated only based on services, not retainer services.
        qs = ServiceActivity.objects.filter(
            Q(status='C') &
            Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        ).values('project_manager__id').annotate(
            total=Count('service__id')
        ).values('project_manager__id', 'total')

        users = []
        for item in qs:
            try:
                user_profile = UserProfile.objects.get(user=item['project_manager__id']) 
            except UserProfile.DoesNotExist:
                continue

            # get the total number of services this user has completed in the last 30 days by querying the ServiceActivity table
            qs = ServiceActivity.objects.filter(
                Q(status='C') &
                Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date) &
                Q(project_manager__id=item['project_manager__id'])
            ).values('service__id').annotate(
                total=Count('service__id')
            ).values('total')

            total_services = 0
            for service in qs:
                total_services += service['total']


            # get the total number of retainer services this user has completed in the last 30 days by querying the RetainerServiceActivity table
            qs_retainer = RetainerServiceActivity.objects.filter(
                Q(status='C') &
                Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date) &
                Q(project_manager_id=item['project_manager__id'])
            ).values('retainer_service__id').annotate(
                total=Count('retainer_service__id')
            ).values('total')

            
            # first get the list of service ids completed with its corresponding job id by this user in the last 30 days
            qs_service = ServiceActivity.objects.filter(
                Q(status='C') &
                Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date) &
                Q(project_manager_id=item['project_manager__id'])
            ).values('service__id', 'job__id')


            # second, query the PriceListEntries table to get the price list entry for each service, and sum up the price
            # the price is based on service, aircraft type, and price_list.
            # With the job_id, get the associated customer and customer settings to find the price list used
            # then get the aircraft type of the job to find the price list entry
            total_revenue = 0
            for service in qs_service:
                job = Job.objects.get(pk=service['job__id'])

                customer_settings = job.customer.customer_settings

                aircraft_type = job.aircraftType

                try:
                    price_list_entry = PriceListEntries.objects.get(
                                                     price_list_id=customer_settings.price_list_id,
                                                     aircraft_type_id=aircraft_type.id,
                                                     service_id=service['service__id'])
                except PriceListEntries.DoesNotExist:
                    continue

                total_revenue += price_list_entry.price


            total_retainer_services = 0
            for item in qs_retainer:
                total_retainer_services += item['total']

            users.append({
                'first_name': user_profile.user.first_name,
                'last_name': user_profile.user.last_name,
                'avatar': user_profile.avatar.url,
                'total_services': total_services,
                'total_retainer_services': total_retainer_services,
                'total_revenue': total_revenue
            })

        # sort users by highest total_revenue
        users = sorted(users, key=lambda k: k['total_revenue'], reverse=True)
           
        
        return Response({
            'total_jobs': total_jobs,
            'total_services': grand_total_services,
            'total_retainer_services': grand_total_retainer_services,
            'total_jobs_price': total_jobs_revenue,
            'top_services': top_services,
            'top_retainer_services': top_retainer_services,
            'users': users
        }, status=status.HTTP_200_OK)








        