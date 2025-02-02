from rest_framework import (permissions, status)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import (
    CustomerAdditionalFeeFBO,
    FBO
)

class FBOCustomerFeesView(APIView):

    def post(self, request):
        fbo_id = request.data.get('fbo_id')
        customer_id = request.data.get('customer_id')

        fees = CustomerAdditionalFeeFBO.objects.filter(customer_additional_fee__customer_setting__customer_id=customer_id,
                                                           customer_additional_fee__type='F',
                                                           fbo_id=fbo_id).all()
        fees_dtos = []

        if not fees:
            fbo = FBO.objects.get(pk=fbo_id)

            f = {
                'fee': fbo.fee,
                'is_percentage': fbo.fee_percentage,
                'amount': fbo.fee
            }

            fees_dtos.append(f)

        else:
            for fee in fees:
                f = {
                    'fee': fee.customer_additional_fee.fee,
                    'is_percentage': fee.customer_additional_fee.percentage,
                    'amount': fee.customer_additional_fee.fee
                }

                fees_dtos.append(f)

        return Response(fees_dtos, status=status.HTTP_200_OK)
