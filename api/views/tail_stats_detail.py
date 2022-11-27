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
        job_service_assignments = JobServiceAssignment.objects.filter(job__tailNumber=tail_number) \
            .order_by('-job__requestDate')[:10]
        
        # get the service name and the updated_at date
        recent_services = job_service_assignments.values('service__name', 'updated_at')


        # get the list of service names with how many times they have been completed for the given tail_number
        # and sort by highest number of jobs first
        service_stats = JobServiceAssignment.objects.values('service__name') \
                                            .filter(job__tailNumber=tail_number) \
                                            .annotate(services_count=Count('service__name')) \
                                            .order_by('-services_count') \
        
        # get the list of retainer service names with how many times they have been completed for the given tail_number
        # and sort by highest number of jobs first
        retainer_service_stats = JobRetainerServiceAssignment.objects.values('retainer_service__name') \
                                            .filter(job__tailNumber=tail_number) \
                                            .annotate(job_count=Count('retainer_service__name')) \
                                            .order_by('-job_count') \

        # get the list of airports with how many times they have been used for the given tail_number
        # and sort by highest number of jobs first
        airport_stats = Job.objects.values('airport__name') \
                                   .filter(tailNumber=tail_number) \
                                   .annotate(job_count=Count('airport__name')) \
                                   .order_by('-job_count') \

        # query the JobStatusActivity table to get the list of users who have worked on the given tail_number
        # and sort by highest number of jobs first
        # The jobs_count IS NOT ACCURATE
        user_stats = JobStatusActivity.objects.values('user__username') \
                                                .filter(job__tailNumber=tail_number) \
                                                .annotate(job_count=Count('user__username')) \
                                                .order_by('-job_count') \


        # get recent JobStatusActivity for this tail number
        recent_activity = JobStatusActivity.objects.filter(job__tailNumber=tail_number).order_by('-timestamp')[:10]


        # Get the total price for all jobs for this tail number
        total_price = Job.objects.filter(tailNumber=tail_number) \
                                 .aggregate(total_price=Sum('price'))

        # Get the total number of jobs for this tail number
        total_jobs = Job.objects.filter(tailNumber=tail_number).count()

        # Get a breakdown by month of how many jobs have been completed for this tail number
        # and sort by month chronological order
        jobs_by_month = Job.objects.filter(tailNumber=tail_number) \
                                      .extra(select={'requestDate': 'EXTRACT(MONTH FROM requestDate)'}) \
                                        .values('requestDate') \
                                        .annotate(job_count=Count('requestDate')) \
                                        .order_by('requestDate')

        # jobs_by_month returns requestDate as a number. Convert to its corresponding month name. For example: 1 = January, 2 = February, etc
        for job in jobs_by_month:
            requestDate = job['requestDate']
            if requestDate == 1:
                job['requestDate'] = 'January'
            elif requestDate == 2:
                job['requestDate'] = 'February'
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
                job['requestDate'] = 'August'
            elif requestDate == 9:
                job['requestDate'] = 'September'
            elif requestDate == 10:
                job['requestDate'] = 'October'
            elif requestDate == 11:
                job['requestDate'] = 'November'
            elif requestDate == 12:
                job['requestDate'] = 'December'

        
        # pass recent_activity to JobActivitySerializer
        activity_serializer = JobActivitySerializer(recent_activity, many=True)

        customer_serializer = CustomerSerializer(customer)

        aircraft_serializer = AircraftTypeSerializer(aircraft_type)


        # Create a json object with all thease values and return it in the response
        return Response({
            'service_stats': service_stats,
            'retainer_service_stats': retainer_service_stats,
            'airport_stats': airport_stats,
            'user_stats': user_stats,
            'recent_activity': activity_serializer.data,
            'customer': customer_serializer.data,
            'aircraft_type': aircraft_serializer.data,
            'total_price': total_price['total_price'],
            'recent_services': recent_services,
            'total_jobs': total_jobs,
            'jobs_by_month': jobs_by_month
        }, status=status.HTTP_200_OK)
