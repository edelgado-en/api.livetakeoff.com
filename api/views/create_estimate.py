from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from datetime import (date, datetime, timedelta)


from api.models import (
        JobEstimate,
        JobServiceEstimate,
        AircraftType,
        Airport,
        FBO,
        UserProfile,
        Service,
        PriceListEntries,
        CustomerDiscount,
        JobEstimateDiscount,
        JobEstimateAdditionalFee,
        Customer
    )


class CreateEstimateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def post(self, request):

        tailNumber = request.data.get('tail_number')
        aircraft_type_id = request.data.get('aircraft_type_id')
        airport_id = request.data.get('airport_id')
        fbo_id = request.data.get('fbo_id')
        customer_id = request.data.get('customer_id')
        show_totals = request.data.get('show_totals')

        s = request.data.get('services')
        services = []

        if s: 
            services = Service.objects.filter(id__in=s)

        # if user is not a customer, get the provided customer
        if request.user.profile.customer:
            customer = request.user.profile.customer
        else:
            customer = Customer.objects.get(id=customer_id)
        

        aircraft_type = AircraftType.objects.get(id=aircraft_type_id)
        airport = Airport.objects.get(id=airport_id)
        selected_fbo = FBO.objects.get(id=fbo_id)

        # get priceListType name
        priceListType = customer.customer_settings.price_list

        # calculate price
        services_price = 0

        # get services with their corresponding prices based on aircraftType and also get the total price
        services_with_prices = []
        for service in services:
            try:
                price = PriceListEntries.objects.get(aircraft_type=aircraft_type,
                                                    price_list=priceListType, service=service).price
                
                services_price += price

            except PriceListEntries.DoesNotExist:
                price = 0

            services_with_prices.append({'id': service.id,
                                      'name': service.name,
                                      'price': price})


        # get discounts for this customer
        discounts = []
        customer_discounts = CustomerDiscount.objects \
                                        .prefetch_related('services') \
                                        .prefetch_related('airports') \
                                        .filter(customer_setting=customer.customer_settings)

        for customer_discount in customer_discounts:
            if customer_discount.type == 'G':
                discounts.append({'id': customer_discount.id, 'name': customer_discount.type,
                                  'discount': customer_discount.discount, 'isPercentage': customer_discount.percentage})
            
            elif customer_discount.type == 'S':
                for service in customer_discount.services.all():
                    if service.service in services:
                        discounts.append({'id': customer_discount.id, 'name': customer_discount.type,
                                          'discount': customer_discount.discount, 'isPercentage': customer_discount.percentage})
                        break
            
            elif customer_discount.type == 'A':
                discounted_airports = customer_discount.airports.all()
                for discounted_airport in discounted_airports:
                    if airport == discounted_airport.airport:
                        discounts.append({'id': customer_discount.id, 'name': customer_discount.type,
                                      'discount': customer_discount.discount, 'isPercentage': customer_discount.percentage})
                        break
        
        
        # get additional fees for this customer
        additional_fees = []
        customer_additional_fees = customer.customer_settings.fees.all()
        
        for customer_additional_fee in customer_additional_fees:
            if customer_additional_fee.type == 'G' or customer_additional_fee.type == 'M':
                additional_fees.append({'id': customer_additional_fee.id, 'name': customer_additional_fee.type,
                                        'fee': customer_additional_fee.fee, 'isPercentage': customer_additional_fee.percentage})
            
            elif customer_additional_fee.type == 'F':
                for fbo in customer_additional_fee.fbos.all():
                    if selected_fbo == fbo.fbo:
                        additional_fees.append({'id': customer_additional_fee.id, 'name': customer_additional_fee.type,
                                                'fee': customer_additional_fee.fee, 'isPercentage': customer_additional_fee.percentage})
                        break

            elif customer_additional_fee.type == 'A':
                upcharged_airports = customer_additional_fee.airports.all()
                for upcharged_airport in upcharged_airports:
                    if airport == upcharged_airport.airport:
                        additional_fees.append({'id': customer_additional_fee.id, 'name': customer_additional_fee.type,
                                            'fee': customer_additional_fee.fee, 'isPercentage': customer_additional_fee.percentage})
                        break

            elif customer_additional_fee.type == 'V':
                upcharged_airports = customer_additional_fee.vendors.all()
                for upcharged_airport in upcharged_airports:
                    if airport == upcharged_airport.airport:
                        additional_fees.append({'id': customer_additional_fee.id, 'name': customer_additional_fee.type,
                                            'fee': customer_additional_fee.fee, 'isPercentage': customer_additional_fee.percentage})
                        break

        # calculate total price discounts first, then additional fees
        total_price = services_price
        
        if total_price > 0:
            for discount in discounts:
                if discount['isPercentage']:
                    total_price -= total_price * discount['discount'] / 100
                else:
                    total_price -= discount['discount']

        discounted_price = total_price

        for additional_fee in additional_fees:
            if additional_fee['isPercentage']:
                if additional_fee['fee'] > 0:
                    dollar_amount = total_price * additional_fee['fee'] / 100
                    
                    additional_fee['additional_fee_dollar_amount'] = dollar_amount

                    total_price += dollar_amount
            
            else:
                dollar_amount = additional_fee['fee']
                
                additional_fee['additional_fee_dollar_amount'] = dollar_amount
                
                total_price += dollar_amount


        job_estimate = JobEstimate.objects.create(
            customer=customer,
            aircraftType=aircraft_type,
            tailNumber=tailNumber,
            requested_by=request.user,
            airport=airport,
            fbo=selected_fbo,
            services_price=services_price,
            discounted_price=discounted_price,
            total_price=total_price,
            show_totals=show_totals,
        )

        # create job service estimates
        for service in services:
            # get the price for the service from services_with_prices array
            price = 0
            for service_with_price in services_with_prices:
                if service_with_price['id'] == service.id:
                    price = service_with_price['price']
                    break

            JobServiceEstimate.objects.create(
                job_estimate=job_estimate,
                service=service,
                price=price
            )

        # create JobEstimateDiscount from discounts array
        for discount in discounts:
            JobEstimateDiscount.objects.create(
                job_estimate=job_estimate,
                amount=discount['discount'],
                percentage=discount['isPercentage'],
                type=discount['name']
            )

        # create JobEstimateAdditionalFee from additional_fees array
        for additional_fee in additional_fees:
            JobEstimateAdditionalFee.objects.create(
                job_estimate=job_estimate,
                amount=additional_fee['fee'],
                percentage=additional_fee['isPercentage'],
                type=additional_fee['name']
            )


        return Response({'id': job_estimate.id}, status=status.HTTP_200_OK)
