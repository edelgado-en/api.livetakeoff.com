from rest_framework import (permissions, status)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import (
    CustomerAdditionalFeeAirport,
    CustomerAdditionalFeeVendor,
    Airport
)

class AirportCustomerFeesView(APIView):

    def post(self, request):
        airport_id = request.data.get('airport_id')
        customer_id = request.data.get('customer_id')

        travel_fees = CustomerAdditionalFeeAirport.objects.filter(customer_additional_fee__customer_setting__customer_id=customer_id,
                                                           customer_additional_fee__type='A',
                                                           airport_id=airport_id).all()
        fees_dtos = []

        # if travel_fees is empty, then use the travel fee from the airport itself
        if not travel_fees:
            airport = Airport.objects.get(pk=airport_id)

            if airport and airport.fee and airport.fee > 0:
                f = {
                    'type': 'A',
                    'fee': airport.fee,
                    'is_percentage': airport.fee_percentage,
                }

                fees_dtos.append(f)
        
        else:
            for fee in travel_fees:
                f = {
                    'type': 'A',
                    'fee': fee.customer_additional_fee.fee,
                    'is_percentage': fee.customer_additional_fee.percentage,
                }

                fees_dtos.append(f)

        vendor_higher_price_fees = CustomerAdditionalFeeVendor.objects.filter(customer_additional_fee__customer_setting__customer_id=customer_id,
                                                           customer_additional_fee__type='V',
                                                           airport_id=airport_id).all()

        for fee in vendor_higher_price_fees:
            f = {
                'type': 'V',
                'fee': fee.customer_additional_fee.fee,
                'is_percentage': fee.customer_additional_fee.percentage,
            }

            fees_dtos.append(f)

        return Response(fees_dtos, status=status.HTTP_200_OK)
