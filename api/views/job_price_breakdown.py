from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User

from api.models import (Job, JobServiceAssignment, PriceListEntries, CustomerDiscount)

class JobPriceBreakdownView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, id):
        if not self.can_see_price_breakdown(request.user):
            return Response({'error': 'You do not have permission to see the price breakdown'}, status=status.HTTP_403_FORBIDDEN)


        job = Job.objects.prefetch_related('job_service_assignments') \
                         .select_related('customer__customer_settings__price_list') \
                         .get(pk=id)

        # get aircraftType name
        aircraftType = job.aircraftType

        # get priceListType name
        priceListType = job.customer.customer_settings.price_list

        # calculate price
        services_price = 0

        # get services with their corresponding prices based on aircraftType
        assigned_services = []
        services = []
        for job_service_assignment in job.job_service_assignments.all():
            service = job_service_assignment.service
            services.append(service)
            
            try:
                price = PriceListEntries.objects.get(aircraft_type=aircraftType,
                                                    price_list=priceListType, service=service).price
                
                services_price += price

            except PriceListEntries.DoesNotExist:
                price = 0

            assigned_services.append({'id': service.id,
                                      'name': service.name,
                                      'price': price})


        # get discounts for this customer
        discounts = []
        customer_discounts = CustomerDiscount.objects \
                                        .prefetch_related('services') \
                                        .prefetch_related('airports') \
                                        .filter(customer_setting=job.customer.customer_settings)

        # we only include the discounts that apply to this job based on discount type
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
                    if job.airport == discounted_airport.airport:
                        discounts.append({'id': customer_discount.id, 'name': customer_discount.type,
                                      'discount': customer_discount.discount, 'isPercentage': customer_discount.percentage})
                        break


        # get additional fees for this customer
        additional_fees = []
        customer_additional_fees = job.customer.customer_settings.fees.all()
        # we only include the additional fees that apply to this job based on fee type
        for customer_additional_fee in customer_additional_fees:
            if customer_additional_fee.type == 'G':
                additional_fees.append({'id': customer_additional_fee.id, 'name': customer_additional_fee.type,
                                        'fee': customer_additional_fee.fee, 'isPercentage': customer_additional_fee.percentage})
            
            elif customer_additional_fee.type == 'F':
                for fbo in customer_additional_fee.fbos.all():
                    if job.fbo == fbo.fbo:
                        additional_fees.append({'id': customer_additional_fee.id, 'name': customer_additional_fee.type,
                                                'fee': customer_additional_fee.fee, 'isPercentage': customer_additional_fee.percentage})
                        break

            elif customer_additional_fee.type == 'A':
                upcharged_airports = customer_additional_fee.airports.all()
                for upcharged_airport in upcharged_airports:
                    if job.airport == upcharged_airport.airport:
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
                total_price += total_price * additional_fee['fee'] / 100
            else:
                total_price += additional_fee['fee']

        price_breakdown = {
            'aircraftType': aircraftType.name,
            'priceListType': priceListType.name.upper(),
            'services': assigned_services,
            'servicesPrice': f'{services_price:,.2f}',
            'discounts': discounts,
            'discountedPrice': f'{discounted_price:,.2f}',
            'additionalFees': additional_fees,
            'totalPrice': f'{total_price:,.2f}',
        }

        
        return Response(price_breakdown, status=status.HTTP_200_OK)


    def can_see_price_breakdown(self, user):
        # TODO: account for customer user. Check for customer settings show_job_price
        if user.is_superuser or user.is_staff or user.groups.filter(name='Account Managers').exists():
            return True
        
        return False