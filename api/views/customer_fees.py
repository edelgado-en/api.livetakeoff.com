from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.models import (
        CustomerAdditionalFee,
        Customer,
        CustomerAdditionalFeeAirport,
        CustomerAdditionalFeeFBO,
        CustomerSettings
    )


class CustomerFeesView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, id):
        customer = get_object_or_404(Customer, pk=id)
        settings = CustomerSettings.objects.get(customer=customer)

        customer_fees = CustomerAdditionalFee.objects.filter(customer_setting=settings)

        fees = []

        for customer_fee in customer_fees:
            fee = {
                'id': customer_fee.id,
                'type': customer_fee.type,
                'fee': customer_fee.fee,
                'is_percentage': customer_fee.percentage
            }
            
            airports = []
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

                    airports.append(a)

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

            fee['airports'] = airports
            fee['fbos'] = fbos

            fees.append(fee)


        return Response(fees, status=status.HTTP_200_OK)


    def post(self, request, id):
        if not self.can_update_customer_fee(request.user):
            return Response({'error': 'You do not have permission to add customer fees'},
                             status=status.HTTP_403_FORBIDDEN)

        customer = get_object_or_404(Customer, pk=id)
        settings = CustomerSettings.objects.get(customer=customer)

        fee = CustomerAdditionalFee.objects.create(
            customer_setting=settings,
            type=request.data['type'],
            fee=request.data['fee'],
            percentage=request.data['is_percentage']
        )

        if request.data['type'] == 'A':
            for airport in request.data['airports']:
                CustomerAdditionalFeeAirport.objects.create(
                    customer_additional_fee=fee,
                    airport_id=airport['id']
                )

        if request.data['type'] == 'F':
            for fbo in request.data['fbos']:
                CustomerAdditionalFeeFBO.objects.create(
                    customer_additional_fee=fee,
                    fbo_id=fbo['id']
                )

        return Response({'id': fee.id}, status=status.HTTP_201_CREATED)



    def delete(self, request, id):
        if not self.can_update_customer_fee(request.user):
            return Response({'error': 'You do not have permission to delete customer fees'},
                             status=status.HTTP_403_FORBIDDEN)

        customer_fee = get_object_or_404(CustomerAdditionalFee, pk=id)
        customer_fee.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


    # Additional fees can only be changed by admins and account managers
    def can_update_customer_fee(self, user):
        if user.is_superuser \
          or user.is_staff \
          or user.groups.filter(name='Account Managers').exists():
           return True

        return False

        