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



        # get the list of service names with how many times they have been completed for the given tail_number
        # and sort by highest number of jobs first
        service_stats = JobServiceAssignment.objects.values('service__name') \
                                            .filter(job__tailNumber=tail_number) \
                                            .annotate(job_count=Count('service__name')) \
                                            .order_by('-job_count') \
                                            #.distinct('service__name')
        
        # get the list of retainer service names with how many times they have been completed for the given tail_number
        # and sort by highest number of jobs first
        retainer_service_stats = JobRetainerServiceAssignment.objects.values('retainer_service__name') \
                                            .filter(job__tailNumber=tail_number) \
                                            .annotate(job_count=Count('retainer_service__name')) \
                                            .order_by('-job_count') \
                                            #.distinct('retainer_service__name')

        # get the list of airports with how many times they have been used for the given tail_number
        # and sort by highest number of jobs first
        airport_stats = Job.objects.values('airport__name') \
                                   .filter(tailNumber=tail_number) \
                                   .annotate(job_count=Count('airport__name')) \
                                   .order_by('-job_count') \
                                   #.distinct('airport__name')

        # query the JobStatusActivity table to get the list of users who have worked on the given tail_number
        # and sort by highest number of jobs first
        user_stats = JobStatusActivity.objects.values('user__username') \
                                                .filter(job__tailNumber=tail_number) \
                                                .annotate(job_count=Count('user__username')) \
                                                .order_by('-job_count') \
                                                #.distinct('user__username')
        


        # get recent JobStatusActivity for this tail number
        recent_activity = JobStatusActivity.objects.filter(job__tailNumber=tail_number).order_by('-timestamp')[:10]


        # Get the total price for all jobs for this tail number
        total_price = Job.objects.filter(tailNumber=tail_number) \
                                 .aggregate(total_price=Sum('price'))

        # Get the total number of jobs for this tail number
        total_jobs = Job.objects.filter(tailNumber=tail_number).count()

        # Get a breakdown of the total number of jobs for this tail number by month and sort it chronologically
        #jobs_by_month = Job.objects.filter(tailNumber=tail_number) \
         #                           .extra(select={'month': 'date_trunc(\'month\', requestDate)'}) \
          #                          .values('month').annotate(job_count=F('month')) \
           #                         .order_by('month') \
                                    #.distinct('month')

        #jobs_by_month = Job.objects.filter(tailNumber=tail_number).extra(select={'month': 'EXTRACT(MONTH FROM created_at)'}).values('month').annotate(job_count=F('month')).order_by('-job_count').distinct('month')
        
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
            'total_jobs': total_jobs,
            #'jobs_by_month': jobs_by_month
        }, status=status.HTTP_200_OK)
