from django.db.models import Q, F
from django.db import models
from django.db.models import Count, Sum, Func
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User

from datetime import (date, datetime, timedelta)

from api.models import (
    ServiceActivity,
    RetainerServiceActivity,
    Job,
    JobStatusActivity,
    UserProfile,
    PriceListEntries,
    JobComments
)


class UserProductivityView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def post(self, request, id):
        if not self.can_view_dashboard(request.user):
            return Response({'error': 'You do not have permission to view this page'}, status=status.HTTP_403_FORBIDDEN)

        user_profile = UserProfile.objects.get(user_id=id)
        user = user_profile.user
        member_since = user.date_joined
        location = user_profile.location

        last_service_date = ServiceActivity.objects.filter(Q(project_manager=user)
                                                           & Q(status='C')).order_by('-timestamp').first()
        
        last_retainer_service_date = RetainerServiceActivity.objects.filter(Q(project_manager=user)
                                                           & Q(status='C')).order_by('-timestamp').first()

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
            if lastMonth.month == 1 or lastMonth.month == 3 \
                 or lastMonth.month == 5 or lastMonth.month == 7 \
                 or lastMonth.month == 8 or lastMonth.month == 10 or lastMonth.month == 12:
                
                end_date = lastMonth.replace(day=31)
            
            elif lastMonth.month == 4 or lastMonth.month == 6 or lastMonth.month == 9 or lastMonth.month == 11:
                end_date = lastMonth.replace(day=30)
            
            else:
                end_date = lastMonth.replace(day=28)

        elif dateSelected == 'lastQuarter':
            today = date.today()
            # get today's month and check it is in the first, second, third or fourth quarter.
            #  if it is first quarter, then get the previous year's last quarter
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



        services_completed = ServiceActivity.objects.filter(Q(project_manager=user)
                                                            & Q(status='C')
                                                            & Q(timestamp__gte=start_date)
                                                            & Q(timestamp__lte=end_date)).count()
        
        retainer_services_completed = RetainerServiceActivity.objects.filter(Q(project_manager=user)
                                                            & Q(status='C')
                                                            & Q(timestamp__gte=start_date)
                                                            & Q(timestamp__lte=end_date)).count()
        
        jobs_completed = JobStatusActivity.objects.filter(Q(user=user)
                                                            & Q(status='C')
                                                            & Q(timestamp__gte=start_date)
                                                            & Q(timestamp__lte=end_date)).count()
        
        photos_uploaded = JobStatusActivity.objects.filter(Q(user=user)
                                                            & Q(activity_type='U')
                                                            & Q(timestamp__gte=start_date)
                                                            & Q(timestamp__lte=end_date)).count()
        
        comments_created = JobComments.objects.filter(Q(author=user)
                                                            & Q(created__gte=start_date)
                                                            & Q(created__lte=end_date)).count()


        top_five_services = ServiceActivity.objects \
                                            .values('service__name') \
                                            .annotate(count=Count('service__id')) \
                                            .filter(Q(project_manager=user) & Q(status='C')
                                                    & Q(timestamp__gte=start_date)
                                                    & Q(timestamp__lte=end_date)) \
                                            .order_by('-count')[:5]

        top_services = []
        for item in top_five_services:
            top_services.append({
                'name': item['service__name'],
                'total': item['count'],
                'percentage': round((item['count'] / services_completed) * 100, 2)
            })

        
        top_five_retainer_services = RetainerServiceActivity.objects \
                                                            .values('retainer_service__name') \
                                                            .annotate(count=Count('retainer_service__id')) \
                                                            .filter(Q(project_manager=user)
                                                                    & Q(status='C')
                                                                    & Q(timestamp__gte=start_date)
                                                                    & Q(timestamp__lte=end_date) ) \
                                                            .order_by('-count')[:5]

        top_retainer_services = []
        for item in top_five_retainer_services:
            top_retainer_services.append({
                'name': item['retainer_service__name'],
                'total': item['count'],
                'percentage': round((item['count'] / retainer_services_completed) * 100, 2)
            })

        
        top_five_aircraft_types = ServiceActivity.objects \
                                                .values('job__aircraftType__name') \
                                                .annotate(count=Count('job__aircraftType__id')) \
                                                .filter(Q(project_manager=user)
                                                        & Q(status='C')
                                                        & Q(timestamp__gte=start_date)
                                                        & Q(timestamp__lte=end_date)) \
                                                .order_by('-count')[:5]

        top_five_airports = ServiceActivity.objects \
                                                .values('job__airport__name') \
                                                .annotate(count=Count('job__airport__id')) \
                                                .filter(Q(project_manager=user) & Q(status='C')
                                                        & Q(timestamp__gte=start_date)
                                                        & Q(timestamp__lte=end_date)) \
                                                .order_by('-count')[:5]


        last_50_services = ServiceActivity.objects.filter(Q(project_manager=user)
                                                        & Q(status='W')
                                                        & Q(timestamp__gte=start_date)
                                                        & Q(timestamp__lte=end_date)).order_by('-timestamp')[:50]

        recent_service_stats = []

        # Iterate through last_50_services and get the corresponding service activity with status C for the same job and service
        for service_activity in last_50_services:
            try:
                service_activity_c = ServiceActivity.objects.filter(Q(job=service_activity.job)
                                                                & Q(service=service_activity.service)
                                                                & Q(status='C')) \
                                                                .first()

                if service_activity_c:
                    # get the service name, job_aircraftType__name, and how long it took to go from status w to status C in hours
                    service_name = service_activity.service.name
                    job_aircraftType_name = service_activity.job.aircraftType.name
                    time_to_complete = (service_activity_c.timestamp - service_activity.timestamp).total_seconds() / 3600

                    # if time_to_complete is negative, switch it to positive
                    if time_to_complete < 0:
                        time_to_complete = time_to_complete * -1

                    if not any(d['service_name'] == service_name and d['job_aircraftType_name'] == job_aircraftType_name for d in recent_service_stats):
                        recent_service_stats.append({'service_name': service_name,
                                                     'job_aircraftType_name': job_aircraftType_name,
                                                     'time_to_complete': time_to_complete})
            
            except ServiceActivity.DoesNotExist:
                continue

        
        
        recent_service_stats_grouped = []
        for item in recent_service_stats:
            if not any(d['service'] == item['service_name'] for d in recent_service_stats_grouped):
                recent_service_stats_grouped.append({'service': item['service_name'], 'stats': []})
            
            for item2 in recent_service_stats_grouped:
                if item2['service'] == item['service_name']:
                    item2['stats'].append({'aircraft': item['job_aircraftType_name'],
                                           'time_to_complete': item['time_to_complete']})

        # each entry in recent_service_stats_grouped should be sorted by time_to_complete
        for item in recent_service_stats_grouped:
            item['stats'] = sorted(item['stats'], key=lambda k: k['time_to_complete'])

        # convert time_to_complete in recent_service_stats_grouped to the following format: xh ym
        for item in recent_service_stats_grouped:
            for item2 in item['stats']:
                item2['time_to_complete'] = '{0}h {1}m'.format(int(item2['time_to_complete']),
                                                               int((item2['time_to_complete'] % 1) * 60))


        vendor_name = ''
        if user_profile.vendor:
            vendor_name = user_profile.vendor.name

        avatar = ''
        if user_profile.avatar:
            avatar = user_profile.avatar.url

        user = {
            'first_name': user_profile.user.first_name,
            'last_name': user_profile.user.last_name,
            'avatar': avatar,
            'vendor': vendor_name,
            'location': location
        }

        # total revenue generated
        qs_service = ServiceActivity.objects.filter(Q(status='C')
                                                    & Q(project_manager_id=user_profile.user)
                                                    & Q(timestamp__gte=start_date)
                                                    & Q(timestamp__lte=end_date)
                                            ).values('service__id', 'job__id')

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
        
        last_retainer = None
        last_service = None

        # if last_retainer_service_date is not None, get the last retainer service date
        if last_retainer_service_date:
            last_retainer = last_retainer_service_date.timestamp

        if last_service_date:
            last_service = last_service_date.timestamp

        return Response({
            'user': user,
            'member_since': member_since,
            'total_revenue': total_revenue,
            'jobs_completed': jobs_completed,
            'services_completed': services_completed,
            'retainers_completed': retainer_services_completed,
            'photos_uploaded': photos_uploaded,
            'comments_created': comments_created,
            'last_service_date': last_service,
            'last_retainer_service_date': last_retainer,
            'top_five_services': top_services,
            'top_five_retainer_services': top_retainer_services,
            'top_five_aircraft_types': top_five_aircraft_types,
            'top_five_airports': top_five_airports,
            'recent_service_stats': recent_service_stats_grouped
        }, status=status.HTTP_200_OK)

    
    def can_view_dashboard(self, user):
        if user.is_superuser or user.is_staff or user.groups.filter(name='Account Managers').exists():
            return True
        
        return False
            


                    
                   

            






