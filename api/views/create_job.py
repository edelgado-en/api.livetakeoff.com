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
        JobPhotos,
        JobServiceAssignment,
        JobRetainerServiceAssignment,
        JobStatusActivity,
        CustomerSettings,
        PriceList,
        PriceListEntries,
        CustomerDiscount,
        CustomerAdditionalFee
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
        on_site = bool(data['on_site'])

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

        s = data['services']
        r = data['retainer_services']
        services = []
        retainer_services = []

        if s: 
            service_ids = data['services'].split(',')
            services = Service.objects.filter(id__in=service_ids)

        if r:
            retainer_service_ids = data['retainer_services'].split(',')
            retainer_services = RetainerService.objects.filter(id__in=retainer_service_ids)

        user = request.user

        today = date.today()
        today_label = datetime.today().strftime('%Y%m%d')

        # Generate purchase order: current day + number of job received that day.
        #  So if today is 2019-01-01 and we have received 3 jobs today already, the purchase order will be 20190101-4
        jobs_created_today = Job.objects.filter(created_at__contains=today).count()

        purchase_order = today_label + '-' + str(jobs_created_today + 1)

        # Calculate price based on aircraft type, customer, services selected, discounts, and additional fees
        # Move this logic to a PriceCalculator class
        customer_settings = CustomerSettings.objects.select_related('price_list').get(customer=customer)

        price_list_entries = PriceListEntries.objects.filter(price_list=customer_settings.price_list,
                                        aircraft_type=aircraft_type,
                                        service__in=services)

        price = 0
        for entry in price_list_entries:
            price += entry.price


        # Now add discounts only if the price is bigger than zero.
        # if there are no price entries for this price list then the price could be zero. There is no need to add discounts in that case.
        if price > 0:
            discounts = CustomerDiscount.objects \
                                        .prefetch_related('services') \
                                        .prefetch_related('airports') \
                                        .filter(customer_setting=customer_settings)

            for discount in discounts:

                if discount.type == 'S':
                    # check if you have matches with the services selected
                    discounted_services = discount.services.all()
                    
                    # if you have at least one match, apply the discount
                    for discounted_service in discounted_services:
                        if discounted_service.service in services:
                            if discount.percentage:
                                price = price - ((price * discount.discount) / 100)
                            else:
                                price -= discount.discount
                            
                            break
                    
                elif discount.type == 'A':
                    # check if you have matches with the aircraft type selected
                    discounted_airports = discount.airports.all()

                    # if you have at least one match, apply the discount
                    for discounted_airport in discounted_airports:
                        if discounted_airport.airport == airport:
                            if discount.percentage:
                                price = price - ((price * discount.discount) / 100)
                            else:
                                price -= discount.discount
                            
                            break

                elif discount.type == 'G':
                    # just apply the discount
                    if discount.percentage:
                        price = price - ((price * discount.discount) / 100)
                    else:
                        price = price - discount.discount


        # Add fees. Fees are pply after discounts
        additional_fees = CustomerAdditionalFee.objects \
                                               .prefetch_related('fbos') \
                                               .prefetch_related('airports') \
                                               .filter(customer_setting=customer_settings)

        for fee in additional_fees:
            if fee.type == 'A':
                # check if you have matches with the airports selected
                upcharged_airports = fee.airports.all()

                # if you have at least one match, apply the fee
                for upcharged_airport in upcharged_airports:
                    if upcharged_airport.airport == airport:
                        if fee.percentage:
                            price = price + ((price * fee.fee) / 100)
                        else:
                            price += fee.fee
                        
                        break
            
            elif fee.type == 'F':
                # check if you have matches with the fbos selected
                upcharged_fbos = fee.fbos.all()

                # if you have at least one match, apply the fee
                for upcharged_fbo in upcharged_fbos:
                    if upcharged_fbo.fbo == fbo:
                        if fee.percentage:
                            price = price + ((price * fee.fee) / 100)
                        else:
                            price += fee.fee
                        
                        break

            elif fee.type == 'G':
                # just apply the fee
                if fee.percentage:
                    price = price + ((price * fee.fee) / 100)
                else:
                    price += fee.fee


        # the price should not be bellow 0
        if price < 0:
            price = 0


        job = Job(purchase_order=purchase_order,
                  customer=customer,
                  tailNumber=tailNumber,
                  price=price,
                  aircraftType=aircraft_type,
                  airport=airport,
                  fbo=fbo,
                  estimatedETA=estimated_arrival_date,
                  estimatedETD=estimated_departure_date,
                  completeBy=complete_by_date,
                  created_by=user,
                  on_site=on_site)

        job.save()

        for service in services:
            assignment = JobServiceAssignment(job=job,service=service)
            assignment.save()

        for retainer_service in retainer_services:
            assignment = JobRetainerServiceAssignment(job=job, retainer_service=retainer_service)
            assignment.save()


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
            
            p = JobPhotos(job=job,
                          uploaded_by=request.user,
                          image=photo,
                          name=name,
                          customer_uploaded=True,
                          size=photo.size)
            p.save()

        # if user is customer, this is submitted, otherwise it is accepted
        JobStatusActivity.objects.create(job=job, user=request.user, status='A')

        response = {
            'id': job.id,
            'purchase_order': job.purchase_order
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
