from django.db.models import Q, F
from django.db import models
from django.db.models import Count, Sum, Func
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User

from datetime import (date, datetime, timedelta)
import pytz
from email.utils import parsedate_tz, mktime_tz

from api.models import (
    ServiceActivity,
    RetainerServiceActivity,
    Job,
    JobStatusActivity,
    UserProfile,
    PriceListEntries,
    JobPhotos,
    JobComments
)


class UserProductivityView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, id):
        if not self.can_view_dashboard(request.user):
            return Response({'error': 'You do not have permission to view this page'}, status=status.HTTP_403_FORBIDDEN)

        # get the user by id
        user_profile = UserProfile.objects.get(user_id=id)

        user = user_profile.user

        # Count how many services the user has completed by querying the serviceActivity table
        # and filtering by the user and the status of the service
        # and then counting the number of services
        services_completed = ServiceActivity.objects.filter(Q(project_manager=user) & Q(status='C')).count()

        #Count how many retainer services the user has completed by querying the retainerServiceActivity table
        # and filtering by the user and the status of the service
        # and then counting the number of services
        retainer_services_completed = RetainerServiceActivity.objects.filter(Q(project_manager=user) & Q(status='C')).count()

        #Count how many jobs the user has completed by querying the jobStatusActivity table
        # and filtering by the user and the status of the job
        # and then counting the number of jobs
        jobs_completed = JobStatusActivity.objects.filter(Q(user=user) & Q(status='C')).count()

        # count how many jobPhotos the user has uploaded by querying the jobPhotos table
        # and filtering by the user
        # and then counting the number of photos
        # This needs to come from JobStatusActivity table activity_type = 'U'
        photos_uploaded = JobStatusActivity.objects.filter(Q(user=user) & Q(activity_type='U')).count()


        #Count how many comments the user has made by querying the jobComments table
        # and filtering by the user
        # and then counting the number of comments
        comments_created = JobComments.objects.filter(Q(author=user)).count()


        # Get the date when this user was created by checking the User table
        # and then converting the date to a string
        #member_since = user.date_joined.strftime("%m/%d/%Y")
        member_since = user.date_joined


        # Get the date of the last service the user completed by querying the serviceActivity table
        # and filtering by the user and the status of the service
        # and then ordering by the timestamp of the service
        # and then getting the first service in the list
        # and then converting the date to a string
        last_service_date = ServiceActivity.objects.filter(Q(project_manager=user) & Q(status='C')).order_by('-timestamp').first()


        # Get the date of the last retainer service the user completed by querying the retainerServiceActivity table
        # and filtering by the user and the status of the service
        # and then ordering by the timestamp of the service
        last_retainer_service_date = RetainerServiceActivity.objects.filter(Q(project_manager=user) & Q(status='C')).order_by('-timestamp').first()

        # Get the last five jobComments the user has made by querying the jobComments table
        # and filtering by the user
        # and then ordering by the timestamp of the comment
        # and then getting the first five comments in the list
        last_five_comments = JobComments.objects.filter(Q(author=user)).order_by('-created')[:5]

        # Get the top 5 services the user has completed by querying the serviceActivity table group by the service and airport
        # and filtering by the user and the status of the service
        # and then ordering by the number of services
        # and then getting the first five services in the list
        top_five_services = ServiceActivity.objects \
                                            .values('service__name') \
                                            .annotate(count=Count('service__id')) \
                                            .filter(Q(project_manager=user) & Q(status='C')) \
                                            .order_by('-count')[:5]

        top_services = []
        # add a percentage value to each service which is calculated based on the top 5 services provided
        for item in top_five_services:
            top_services.append({
                'name': item['service__name'],
                'total': item['count'],
                'percentage': round((item['count'] / services_completed) * 100, 2)
            })

        
        # Get the top 5 retainer services the user has completed by querying the retainerServiceActivity table group by the service and airport
        # and filtering by the user and the status of the service
        # and then ordering by the number of services
        # and then getting the first five services in the list
        top_five_retainer_services = RetainerServiceActivity.objects \
                                                            .values('retainer_service__name') \
                                                            .annotate(count=Count('retainer_service__id')) \
                                                            .filter(Q(project_manager=user) & Q(status='C')) \
                                                            .order_by('-count')[:5]

        top_retainer_services = []
        # add a percentage value to each retainer service which is calculated based on the top 5 retainer services provided
        for item in top_five_retainer_services:
            top_retainer_services.append({
                'name': item['retainer_service__name'],
                'total': item['count'],
                'percentage': round((item['count'] / retainer_services_completed) * 100, 2)
            })

        
        # Get the top 5 aircarft types the user has completed services for by querying the serviceActivity table group by the job__aircraftType
        # and filtering by the user and the status of the service
        # and then ordering by the number of services
        # and then getting the first five aircraft types in the list
        # the resultset should look like this: aircraftType__name, services_completed
        top_five_aircraft_types = ServiceActivity.objects \
                                                .values('job__aircraftType__name') \
                                                .annotate(count=Count('job__aircraftType__id')) \
                                                .filter(Q(project_manager=user) & Q(status='C')) \
                                                .order_by('-count')[:5]

        # Get the top 5 airports the user has completed services for by querying the serviceActivity table group by the job__airport
        # and filtering by the user and the status of the service
        # and then ordering by the number of services
        # and then getting the first five airports in the list
        top_five_airports = ServiceActivity.objects \
                                                .values('job__airport__name') \
                                                .annotate(count=Count('job__airport__id')) \
                                                .filter(Q(project_manager=user) & Q(status='C')) \
                                                .order_by('-count')[:5]

        
        # Get the last 100 services with status W by the user by querying the serviceActivity table
        # and filtering by the user and the status of the service
        # and then ordering by the timestamp of the service
        # and then getting the first 100 services in the list
        last_50_services = ServiceActivity.objects.filter(Q(project_manager=user) & Q(status='W')).order_by('-timestamp')[:50]

        recent_service_stats = []

        # Iterate through last_100_services and get the corresponding service activity with status C for the same job and service
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

                    # append the service name, job_aircraftType__name, and how long it took to go from status w to status C in hours to the recent_service_stats list
                    
                    #only append if an entry for this service_name and job_aircraftType_name does not already exist
                    if not any(d['service_name'] == service_name and d['job_aircraftType_name'] == job_aircraftType_name for d in recent_service_stats):
                        recent_service_stats.append({'service_name': service_name, 'job_aircraftType_name': job_aircraftType_name, 'time_to_complete': time_to_complete})
                    #recent_service_stats.append([service_name, job_aircraftType_name, time_to_complete])
            
            except ServiceActivity.DoesNotExist:
                continue

        
        # create an array out of recent_service_stats where data is grouped by service_name.
        #  Each entry of the array should look like this:
        # {service: service_name, stats: [{"aircraft":job_aircraftType_name, "time_to_complete": time_to_complete}]
        #  }
        recent_service_stats_grouped = []
        for item in recent_service_stats:
            if not any(d['service'] == item['service_name'] for d in recent_service_stats_grouped):
                recent_service_stats_grouped.append({'service': item['service_name'], 'stats': []})
            
            for item2 in recent_service_stats_grouped:
                if item2['service'] == item['service_name']:
                    item2['stats'].append({'aircraft': item['job_aircraftType_name'], 'time_to_complete': item['time_to_complete']})

        # each entry in recent_service_stats_grouped should be sorted by time_to_complete
        for item in recent_service_stats_grouped:
            item['stats'] = sorted(item['stats'], key=lambda k: k['time_to_complete'])

        # convert time_to_complete in recent_service_stats_grouped to the following format: xh ym
        for item in recent_service_stats_grouped:
            for item2 in item['stats']:
                item2['time_to_complete'] = '{0}h {1}m'.format(int(item2['time_to_complete']), int((item2['time_to_complete'] % 1) * 60))


        comments = []
        #iterate through last_five_comments and get the comment and date and append to comments list
        for comment in last_five_comments:
            comments.append([comment.comment, comment.created])

        vendor_name = ''

        if user_profile.vendor:
            vendor_name = user_profile.vendor.name

        user = {
            'first_name': user_profile.user.first_name,
            'last_name': user_profile.user.last_name,
            'avatar': user_profile.avatar.url,
            'vendor': vendor_name
        }

        # total revenue generated
        qs_service = ServiceActivity.objects.filter(
                Q(status='C') &
                Q(project_manager_id=user_profile.user)
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

        return Response({
            'user': user,
            'member_since': member_since,
            'total_revenue': total_revenue,
            'jobs_completed': jobs_completed,
            'services_completed': services_completed,
            'retainers_completed': retainer_services_completed,
            'photos_uploaded': photos_uploaded,
            'comments_created': comments_created,
            'last_service_date': last_service_date.timestamp,
            'last_retainer_service_date': last_retainer_service_date.timestamp,
            'top_five_services': top_services,
            'top_five_retainer_services': top_retainer_services,
            'top_five_aircraft_types': top_five_aircraft_types,
            'top_five_airports': top_five_airports,
            'recent_service_stats': recent_service_stats_grouped,
            'last_five_comments': comments,
        }, status=status.HTTP_200_OK)

    

    def can_view_dashboard(self, user):
        if user.is_superuser or user.is_staff or user.groups.filter(name='Account Managers').exists():
            return True
        
        return False
            


                    
                   

            






