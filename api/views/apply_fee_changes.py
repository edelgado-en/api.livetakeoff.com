from rest_framework import (permissions, status)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import (
    Airport,
    FBO
)

class ApplyFeeChangesView(APIView):

    def post(self, request):
        amount = request.data.get('amount')
        amount_type = request.data.get('amount_type')
        airport_ids = request.data.get('airport_ids')
        fbo_ids = request.data.get('fbo_ids')

        if not amount or not amount_type or not (airport_ids or fbo_ids):
            return Response({'error': 'Missing required parameters'}, status=status.HTTP_400_BAD_REQUEST)
        
        # fixed or percentage
        if amount_type not in ['F', 'P']:
            return Response({'error': 'Invalid amount type'}, status=status.HTTP_400_BAD_REQUEST)
        
        if airport_ids:
            airports = Airport.objects.filter(id__in=airport_ids)

            for airport in airports:
                airport.fee = amount
                airport.fee_percentage = True if amount_type == 'P' else False
                airport.save()

        elif fbo_ids:
            fbos = FBO.objects.filter(id__in=fbo_ids)

            for fbo in fbos:
                fbo.fee = amount
                fbo.fee_percentage = True if amount_type == 'P' else False
                fbo.save()

        return Response({'message': 'Fee changes applied successfully'}, status=status.HTTP_200_OK)