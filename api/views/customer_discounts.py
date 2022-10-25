from django.shortcuts import get_object_or_404
from requests import delete
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.models import (
        CustomerDiscount,
        Customer,
        CustomerDiscountService,
        CustomerDiscountAirport,
        CustomerSettings
    )

from api.serializers import CustomerSettingsSerializer


class CustomerDiscountView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, id):
        customer = get_object_or_404(Customer, pk=id)
        settings = CustomerSettings.objects.get(customer=customer)

        customer_discounts = CustomerDiscount.objects.filter(customer_setting=settings)

        discounts = []


        for customer_discount in customer_discounts:
            discount = {
                'id': customer_discount.id,
                'type': customer_discount.type,
                'discount': customer_discount.discount,
                'is_percentage': customer_discount.percentage
            }
            
            services = []
            airports = []

            if customer_discount.type == 'S':
                customer_discount_services = CustomerDiscountService.objects.select_related('service').filter(customer_discount=customer_discount)
                customer_discount.discounted_services = customer_discount_services

                for service in customer_discount_services:
                    s = {
                        'id': service.service.id,
                        'name': service.service.name
                    }

                    services.append(s)

            if customer_discount.type == 'A':
                customer_discount_airports = CustomerDiscountAirport.objects.select_related('airport').filter(customer_discount=customer_discount)
                customer_discount.discounted_airports = customer_discount_airports

                for airport in customer_discount_airports:
                    a = {
                        'id': airport.airport.id,
                        'name': airport.airport.name
                    }

                    airports.append(a)

            discount['services'] = services
            discount['airports'] = airports

            discounts.append(discount)

        return Response(discounts, status=status.HTTP_200_OK)


    def post(self, request, id):
        if not self.can_update_customer_discount(request.user):
            return Response({'error': 'You do not have permission to create customer discounts'},
                             status=status.HTTP_403_FORBIDDEN)

        # TODO: validate discount is only numbers

        customer = get_object_or_404(Customer, pk=id)
        settings = CustomerSettings.objects.get(customer=customer)

        customer_discount = CustomerDiscount(customer_setting=settings,
                                         discount=request.data['discount'],
                                         percentage=request.data['is_percentage'],
                                         type=request.data['type'])

        customer_discount.save()

        if request.data['type'] == 'S':
            for service in request.data['services']:
                customer_discount_service = CustomerDiscountService(customer_discount=customer_discount,
                                                                    service_id=service['id'])

                customer_discount_service.save()


        if request.data['type'] == 'A':
            for airport in request.data['airports']:
                customer_discount_airport = CustomerDiscountAirport(customer_discount=customer_discount,
                                                                    airport_id=airport['id'])

                customer_discount_airport.save()

        return Response({'id': customer_discount.id}, status=status.HTTP_201_CREATED)
      

    def delete(self, request, id):
        if not self.can_update_customer_discount(request.user):
            return Response({'error': 'You do not have permission to delete customer discounts'},
                             status=status.HTTP_403_FORBIDDEN)

        customer_discount = get_object_or_404(CustomerDiscount, pk=id)
        customer_discount.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


    # Discounts can only be changed by admins and account managers
    def can_update_customer_discount(self, user):
        if user.is_superuser \
          or user.is_staff \
          or user.groups.filter(name='Account Managers').exists():
           return True

        return False


