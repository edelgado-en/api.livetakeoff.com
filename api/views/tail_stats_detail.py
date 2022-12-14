from django.db.models import Q, F
from django.db import models
from django.db.models import Count, Sum, Func
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.models import (
    JobServiceAssignment,
    JobRetainerServiceAssignment,
    Job,
    Airport,
    UserProfile,
    JobStatusActivity,
    ServiceActivity,
    RetainerServiceActivity
)

from api.serializers import (JobActivitySerializer, CustomerSerializer, AircraftTypeSerializer)

class Month(Func):
    function = 'EXTRACT'
    template = '%(function)s(MONTH FROM %(expressions)s)'
    output_field = models.IntegerField()

class Year(Func):
    function = 'EXTRACT'
    template = '%(function)s(YEAR FROM %(expressions)s)'
    output_field = models.IntegerField()


class TailStatsDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, tail_number):
        # if the tail does not exists, then throw an error
        customer = None
        aircraft_type = None

        try:
            # if the current user is a customer, then only show the stats for that customer
            if request.user.profile.customer:
                job = Job.objects.filter(tailNumber=tail_number, customer=request.user.profile.customer).order_by('-requestDate')[:1]

            else:
                job = Job.objects.filter(tailNumber=tail_number).order_by('-requestDate')[:1]


            for j in job:
                customer = j.customer
                aircraft_type = j.aircraftType

        except Job.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


        # get the list of the last 10 services for the given tail number with their corresponding dates
        # and sort by most recent date first
        # query the ServiceActivity table
        service_activity = ServiceActivity.objects.filter(job__tailNumber=tail_number, status='C').order_by('-timestamp')[:10]

        
        # get the service name and the updated_at date
        recent_services = service_activity.values('service__name', 'timestamp')
        
        # get the list of the last 10 retainer services for the given tail number with their corresponding dates
        # and sort by most recent date first
        # qeury the RetainerServiceActivity table
        retainer_service_activity = RetainerServiceActivity.objects.filter(job__tailNumber=tail_number, status='C').order_by('-timestamp')[:10]

        
        # get the retainer service name and the updated_at date
        recent_retainer_services = retainer_service_activity.values('retainer_service__name', 'timestamp')


        # get the list of service names with how many times they have been completed for the given tail_number
        # and sort by highest number of services first. This should only include status completed (C)
        # query the ServiceActivity table
        service_stats = ServiceActivity.objects.filter(job__tailNumber=tail_number, status='C') \
                                                  .values('service__name') \
                                                  .annotate(services_count=Count('service__name')) \
                                                  .order_by('-services_count')

        # get the list of retainer service names with how many times they have been completed for the given tail_number
        # and sort by highest number of services first
        # query the RetainerServiceActivity table
        retainer_service_stats = RetainerServiceActivity.objects.filter(job__tailNumber=tail_number, status='C') \
                                                                    .values('retainer_service__name') \
                                                                    .annotate(services_count=Count('retainer_service__name')) \
                                                                    .order_by('-services_count')


        # get the list of airports with how many times they have been used for the given tail_number
        # and sort by highest number of jobs first
        airport_stats = Job.objects.values('airport__name') \
                                   .filter(tailNumber=tail_number, status__in=['C', 'W', 'I']) \
                                   .annotate(job_count=Count('airport__name')) \
                                   .order_by('-job_count') \

        # query the JobStatusActivity table to get the list of project managers with how many times a job has been set to status Complete (C)
        # and sort by highest number of jobs first
        # need to include the user's avatar from the UserProfile table
        project_manager_stats = JobStatusActivity.objects.values('user__username', 'user__first_name', 'user__last_name', 'user__profile__avatar') \
                                                            .filter(job__tailNumber=tail_number, status='C') \
                                                            .annotate(job_count=Count('user__username')) \
                                                            .order_by('-job_count') \


        # get recent JobStatusActivity for this tail number
        recent_activity = JobStatusActivity.objects.filter(job__tailNumber=tail_number)

        # is user is a customer exclude job status canceled (T) from recent_activity
        if request.user.profile.customer:
            recent_activity = recent_activity.exclude(status='T')


        if request.user.profile.customer:
            recent_activity = recent_activity.exclude(Q(status='P') | Q(activity_type='P'))

        recent_activity = recent_activity.order_by('-timestamp')[:20]

        # Get the total price for all jobs for this tail number only including status completed and invoiced
        if request.user.is_superuser \
                 or request.user.is_staff \
                 or request.user.groups.filter(name='Account Managers').exists() \
                 or (request.user.profile.customer and self.request.user.profile.customer.customer_settings.show_spending_info):
            
            total_price = Job.objects.filter(tailNumber=tail_number, status__in=['I']) \
                                 .aggregate(total_price=Sum('price'))

            if not total_price['total_price']:
                total_price = 0
            else:
                total_price = total_price['total_price']
        
        else:
            total_price = 0


        # Get the total number of jobs for this tail number
        total_jobs = Job.objects.filter(tailNumber=tail_number)

        if self.request.user.profile.customer:
            total_jobs = total_jobs.exclude(status='T')
        
        total_jobs = total_jobs.count()

        # get the total number of invoiced jobs for this tail number
        total_invoiced_jobs = Job.objects.filter(tailNumber=tail_number, status='I').count()

        # get the total number of completed jobs for this tail number
        total_completed_jobs = Job.objects.filter(tailNumber=tail_number, status='C').count()

        # get the total number of canceled jobs for this tail number
        total_canceled_jobs = Job.objects.filter(tailNumber=tail_number, status='T').count()

        # get the total number of open jobs for this tail number. An open job is a job with status U or A or S or W
        total_open_jobs = Job.objects.filter(tailNumber=tail_number, status__in=['U', 'A', 'S', 'W']).count()


        jobs_by_month = Job.objects.filter(status__in=['C', 'I'], tailNumber=tail_number) \
                                   .annotate(month=Month('requestDate')) \
                                   .annotate(year=Year('requestDate')) \
                                   .values('month', 'year') \
                                   .annotate(job_count=Count('month')) \
                                   .order_by('month')

        # create a dictionary where they key is the year and the value is a list of jobs by month with its corresponding year
        jobs_by_month_dict = {}
        for job in jobs_by_month:
            if job['year'] not in jobs_by_month_dict:
                jobs_by_month_dict[job['year']] = []

            jobs_by_month_dict[job['year']].append(job)

        
        # jobs_by_month returns requestDate as a number. Convert to its corresponding month name. For example: 1 = January, 2 = February, etc
        for job in jobs_by_month:
            requestDate = job['month']
            if requestDate == 1:
                job['month'] = 'Jan'
            elif requestDate == 2:
                job['month'] = 'Feb'
            elif requestDate == 3:
                job['month'] = 'March'
            elif requestDate == 4:
                job['month'] = 'April'
            elif requestDate == 5:
                job['month'] = 'May'
            elif requestDate == 6:
                job['month'] = 'June'
            elif requestDate == 7:
                job['month'] = 'July'
            elif requestDate == 8:
                job['month'] = 'Aug'
            elif requestDate == 9:
                job['month'] = 'Sept'
            elif requestDate == 10:
                job['month'] = 'Oct'
            elif requestDate == 11:
                job['month'] = 'Nov'
            elif requestDate == 12:
                job['month'] = 'Dec'

        
        # pass recent_activity to JobActivitySerializer
        activity_serializer = JobActivitySerializer(recent_activity, many=True)

        customer_serializer = CustomerSerializer(customer)

        aircraft_serializer = AircraftTypeSerializer(aircraft_type)

        #Get the requestDate column value of the first job for this tail number
        first_job_date = Job.objects.filter(tailNumber=tail_number).order_by('requestDate')[:1].values('requestDate')


        # Create a json object with all thease values and return it in the response
        return Response({
            'tailNumber': tail_number,
            'first_job_date': first_job_date,
            'service_stats': service_stats,
            'retainer_service_stats': retainer_service_stats,
            'airport_stats': airport_stats,
            'project_manager_stats': project_manager_stats,
            'recent_activity': activity_serializer.data,
            'customer': customer_serializer.data,
            'aircraft_type': aircraft_serializer.data,
            'total_price': total_price,
            'recent_services': recent_services,
            'recent_retainer_services': recent_retainer_services,
            'total_jobs': total_jobs,
            'total_invoiced_jobs': total_invoiced_jobs,
            'total_completed_jobs': total_completed_jobs,
            'total_canceled_jobs': total_canceled_jobs,
            'total_open_jobs': total_open_jobs,
            'jobs_by_month': jobs_by_month,
            'jobs_by_year': jobs_by_month_dict
        }, status=status.HTTP_200_OK)
