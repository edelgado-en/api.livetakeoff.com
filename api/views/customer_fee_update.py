from django.shortcuts import get_object_or_404
from requests import delete
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.models import (
        CustomerAdditionalFee,
        CustomerAdditionalFeeAirport,
        CustomerAdditionalFeeVendor,
        CustomerAdditionalFeeFBO,
    )


class CustomerFeeUpdateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        customer_fee = get_object_or_404(CustomerAdditionalFee, pk=id)

        fee = {
            'id': customer_fee.id,
            'type': customer_fee.type,
            'fee': customer_fee.fee,
            'is_percentage': customer_fee.percentage
        }
            
        travel_fees_airports = []
        vendor_higher_price_airports = []
        fbos = []

        if customer_fee.type == 'A':
            customer_fee_airports = CustomerAdditionalFeeAirport.objects \
                                            .select_related('airport') \
                                            .filter(customer_additional_fee=customer_fee)

            for airport in customer_fee_airports:
                a = {
                    'id': airport.airport.id,
                    'name': airport.airport.name
                }

                travel_fees_airports.append(a)

        if customer_fee.type == 'V':
            customer_fee_airports = CustomerAdditionalFeeVendor.objects \
                                            .select_related('airport') \
                                            .filter(customer_additional_fee=customer_fee)

            for airport in customer_fee_airports:
                a = {
                    'id': airport.airport.id,
                    'name': airport.airport.name
                }

                vendor_higher_price_airports.append(a)

        if customer_fee.type == 'F':
            customer_fee_fbo = CustomerAdditionalFeeFBO.objects \
                                            .select_related('fbo') \
                                            .filter(customer_additional_fee=customer_fee)

            for f in customer_fee_fbo:
                f = {
                    'id': f.fbo.id,
                    'name': f.fbo.name
                }

                fbos.append(f)

        fee['travel_fees_airports'] = travel_fees_airports
        fee['vendor_higher_price_airports'] = vendor_higher_price_airports
        fee['fbos'] = fbos

        return Response(fee, status=status.HTTP_200_OK)


    def patch(self, request, id):
        if not self.can_update_customer_fee(request.user):
            return Response({'error': 'You do not have permission to update customer fees'},
                             status=status.HTTP_403_FORBIDDEN)

        customer_fee = get_object_or_404(CustomerAdditionalFee, pk=id)

        customer_fee.fee = request.data.get('fee')
        customer_fee.percentage = request.data.get('is_percentage')
        customer_fee.type = request.data.get('type')

        customer_fee.save()

        if customer_fee.type == 'A':
            CustomerAdditionalFeeAirport.objects.filter(customer_additional_fee=customer_fee).delete()

            for airport in request.data.get('airports'):
                CustomerAdditionalFeeAirport.objects.create(
                    customer_additional_fee=customer_fee,
                    airport_id=airport.get('id')
                )

        if customer_fee.type == 'V':
            CustomerAdditionalFeeVendor.objects.filter(customer_additional_fee=customer_fee).delete()

            for airport in request.data.get('airports'):
                CustomerAdditionalFeeVendor.objects.create(
                    customer_additional_fee=customer_fee,
                    airport_id=airport.get('id')
                )

        if customer_fee.type == 'F':
            CustomerAdditionalFeeFBO.objects.filter(customer_additional_fee=customer_fee).delete()

            for fbo in request.data.get('fbos'):
                CustomerAdditionalFeeFBO.objects.create(
                    customer_additional_fee=customer_fee,
                    fbo_id=fbo.get('id')
                )

        return Response({'message': 'success'}, status=status.HTTP_200_OK)


    def can_update_customer_fee(self, user):
        if user.is_superuser \
          or user.is_staff \
          or user.groups.filter(name='Account Managers').exists():
           return True

        return False