from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from datetime import (date, datetime, timedelta)
from email.utils import parsedate_tz, mktime_tz

from ..models import (
    Job,
    Service,
    RetainerService,
    AircraftType,
    Airport,
    Customer,
    FBO,
    JobComments,
    JobPhotos
    )


class CreateJobView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):

        if not self.can_create_job(request.user):
            return Response({'error': 'You do not have permission to create a job'}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data

        tailNumber = data['tail_number']
        customer = get_object_or_404(Customer, pk=data['customer_id'])
        aircraft_type = get_object_or_404(AircraftType, pk=data['aircraft_type_id'])
        airport = get_object_or_404(Airport, pk=data['airport_id'])
        fbo = get_object_or_404(FBO, pk=data['fbo_id'])


        estimated_arrival_date = data['estimated_arrival_date']
        if estimated_arrival_date == 'null':
            estimated_arrival_date = None
        else :
            try:
                timestamp = mktime_tz(parsedate_tz(estimated_arrival_date))
                # Now it is in UTC
                estimated_arrival_date = datetime(1970, 1, 1) + timedelta(seconds=timestamp)
            
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST)


        estimated_departure_date = data['estimated_departure_date']
        if estimated_departure_date == 'null':
            estimated_departure_date = None
        else :
            try:
                timestamp = mktime_tz(parsedate_tz(estimated_departure_date))
                # Now it is in UTC
                estimated_departure_date = datetime(1970, 1, 1) + timedelta(seconds=timestamp)
            
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST)


        complete_by_date = data['complete_by_date']
        if complete_by_date == 'null':
            complete_by_date = None
        else:
            try:
                timestamp = mktime_tz(parsedate_tz(complete_by_date))
                # Now it is in UTC
                complete_by_date = datetime(1970, 1, 1) + timedelta(seconds=timestamp)
            
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST)


        comment = data['comment']

        service_ids = data['services'].split(',')
        services = []

        if service_ids:
            services = Service.objects.filter(id__in=service_ids)

        retainer_service_ids = data['retainer_services'].split(',')
        retainer_services = []

        if retainer_service_ids:
            retainer_services = RetainerService.objects.filter(id__in=retainer_service_ids)

        user = request.user

        today = date.today()
        today_label = datetime.today().strftime('%Y%m%d')

        # Generate purchase order: current day + number of job received that day.
        #  So if today is 2019-01-01 and we have received 3 jobs today already, the purchase order will be 20190101-4
        jobs_created_today = Job.objects.filter(created_at__contains=today).count()

        purchase_order = today_label + '-' + str(jobs_created_today + 1)

        job = Job(purchase_order=purchase_order,
                  customer=customer,
                  tailNumber=tailNumber,
                  aircraftType=aircraft_type,
                  airport=airport,
                  fbo=fbo,
                  estimatedETA=estimated_arrival_date,
                  estimatedETD=estimated_departure_date,
                  completeBy=complete_by_date,
                  created_by=user)

        job.save()
        job.services.add(*services)
        job.retainerServices.add(*retainer_services)


        # TODO: Calculate estimated completion time based on the estimated times of the selected services and aircraft type

        if comment:
            job_comment = JobComments(job=job,
                                    comment=comment,
                                    author=user)
            job_comment.save()        

        
        name = job.tailNumber + '_' + job.airport.initials + '_' + datetime.today().strftime('%Y-%m-%d')
        counter = 0
        for photo in request.data.getlist('image'):
            name = name + '_' + str(counter)
            
            # TODO: NEED TO ADD A NEW COLUMN TO THE JOB PHOTOS TO SAY IF IT CUSTOMER UPLOAD OR NOT
            p = JobPhotos(job=job,
                          uploaded_by=request.user,
                          image=photo,
                          name=name,
                          size=photo.size)
            p.save()


        response = {
            'id': job.id,
        }

        return Response(response, status.HTTP_201_CREATED)



    def can_create_job(self, user):
        """
        Check if the user has permission to create a job.
        """
        if user.is_superuser or user.is_staff or user.groups.filter(name='Account Managers').exists():
            return True
        else:
            return False
