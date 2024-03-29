from rest_framework import (permissions, status)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import (
    CustomerAdditionalFeeAirport
)

class AirportCustomerFeesView(APIView):

    def post(self, request):
        airport_id = request.data.get('airport_id')
        customer_id = request.data.get('customer_id')

        fees = CustomerAdditionalFeeAirport.objects.filter(customer_additional_fee__customer_setting__customer_id=customer_id,
                                                           customer_additional_fee__type='A',
                                                           airport_id=airport_id).all()
        fees_dtos = []

        for fee in fees:
            f = {
                'fee': fee.customer_additional_fee.fee,
                'is_percentage': fee.customer_additional_fee.percentage,
            }

            fees_dtos.append(f)

        return Response(fees_dtos, status=status.HTTP_200_OK)
