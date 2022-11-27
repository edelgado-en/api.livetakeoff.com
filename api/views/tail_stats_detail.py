from django.db.models import Q, F
from django.db.models import Count, Sum
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
    JobStatusActivity
)

from api.serializers import (JobActivitySerializer, CustomerSerializer, AircraftTypeSerializer)


class TailStatsDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, tail_number):
        # if the tail does not exists, then throw an error
        customer = None
        aircraft_type = None
        try:
            job = Job.objects.filter(tailNumber=tail_number).order_by('-requestDate')[:1]

            for j in job:
                customer = j.customer
                aircraft_type = j.aircraftType
                break

        except Job.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


        # get the list of the last 10 services for the given tail number with their corresponding dates
        # and sort by most recent date first
        job_service_assignments = JobServiceAssignment.objects.filter(job__tailNumber=tail_number, status__in=['C', 'W']) \
            .order_by('-job__requestDate')[:10]
        
        # get the service name and the updated_at date
        recent_services = job_service_assignments.values('service__name', 'updated_at')
        
        # get the list of the last 10 retainer services for the given tail number with their corresponding dates
        # and sort by most recent date first
        job_retainer_service_assignments = JobRetainerServiceAssignment.objects.filter(job__tailNumber=tail_number, status__in=['C', 'W']) \
            .order_by('-job__requestDate')[:10]
        
        # get the retainer service name and the updated_at date
        recent_retainer_services = job_retainer_service_assignments.values('retainer_service__name', 'updated_at')


        # get the list of service names with how many times they have been completed for the given tail_number
        # and sort by highest number of jobs first. This should only include status completed (C) or W
        service_stats = JobServiceAssignment.objects.values('service__name') \
                                            .filter(job__tailNumber=tail_number, status__in=['C', 'W']) \
                                            .annotate(services_count=Count('service__name')) \
                                            .order_by('-services_count') \
        
        # get the list of retainer service names with how many times they have been completed for the given tail_number
        # and sort by highest number of jobs first
        retainer_service_stats = JobRetainerServiceAssignment.objects.values('retainer_service__name') \
                                            .filter(job__tailNumber=tail_number, status__in=['C', 'W']) \
                                            .annotate(services_count=Count('retainer_service__name')) \
                                            .order_by('-services_count') \

        # get the list of airports with how many times they have been used for the given tail_number
        # and sort by highest number of jobs first
        airport_stats = Job.objects.values('airport__name') \
                                   .filter(tailNumber=tail_number) \
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
        recent_activity = JobStatusActivity.objects.filter(job__tailNumber=tail_number).order_by('-timestamp')[:10]


        # Get the total price for all jobs for this tail number only including status completed and invoiced
        total_price = Job.objects.filter(tailNumber=tail_number, status__in=['C', 'I']) \
                                 .aggregate(total_price=Sum('price'))

        # Get the total number of jobs for this tail number
        total_jobs = Job.objects.filter(tailNumber=tail_number).count()

        # get the total number of canceled jobs for this tail number
        total_canceled_jobs = Job.objects.filter(tailNumber=tail_number, status='T').count()

        # Get a breakdown by month of how many jobs have been completed for this tail number
        # and sort by month chronological order
        # MONTH from api_job.requestDate is failing in Postgres Heroku

        # Get a breakdown of how many jobs have been completed or invoiced for this tail number group by month
        # and sort by month chronological order
        # MONTH from api_job.requestDate is failing in Postgres Heroku

        
        







        """ jobs_by_month = Job.objects.filter(tailNumber=tail_number) \
                                      .extra(select={'requestDate': 'EXTRACT(MONTH FROM api_job.requestDate)'}) \
                                        .values('requestDate') \
                                        .annotate(job_count=Count('requestDate')) \
                                        .order_by('requestDate') """

        # jobs_by_month returns requestDate as a number. Convert to its corresponding month name. For example: 1 = January, 2 = February, etc
        """ for job in jobs_by_month:
            requestDate = job['requestDate']
            if requestDate == 1:
                job['requestDate'] = 'Jan'
            elif requestDate == 2:
                job['requestDate'] = 'Feb'
            elif requestDate == 3:
                job['requestDate'] = 'March'
            elif requestDate == 4:
                job['requestDate'] = 'April'
            elif requestDate == 5:
                job['requestDate'] = 'May'
            elif requestDate == 6:
                job['requestDate'] = 'June'
            elif requestDate == 7:
                job['requestDate'] = 'July'
            elif requestDate == 8:
                job['requestDate'] = 'Aug'
            elif requestDate == 9:
                job['requestDate'] = 'Sept'
            elif requestDate == 10:
                job['requestDate'] = 'Oct'
            elif requestDate == 11:
                job['requestDate'] = 'Nov'
            elif requestDate == 12:
                job['requestDate'] = 'Dec' """

        
        # pass recent_activity to JobActivitySerializer
        activity_serializer = JobActivitySerializer(recent_activity, many=True)

        customer_serializer = CustomerSerializer(customer)

        aircraft_serializer = AircraftTypeSerializer(aircraft_type)

        #Get the requestDate column value of the first job for this tail number
        first_job_date = Job.objects.filter(tailNumber=tail_number).order_by('requestDate')[:1].values('requestDate')

        if not total_price['total_price']:
            total_price = 0
        else:
            total_price = total_price['total_price']

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
            'total_canceled_jobs': total_canceled_jobs
            #'jobs_by_month': jobs_by_month
        }, status=status.HTTP_200_OK)
