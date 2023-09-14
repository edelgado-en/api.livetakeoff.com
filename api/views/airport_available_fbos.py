from rest_framework import (permissions, status)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import (
    AirportAvailableFbo,
    Airport
)

class AirportAvailableFbosView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        airport = Airport.objects.get(pk=id)
        airport_available_fbos = airport.available_fbos.all()

        data = []
        for airport_available_fbo in airport_available_fbos:
            fbo = airport_available_fbo.fbo
            data.append({
                'id': fbo.id,
                'name': fbo.name
            })

        return Response(data, status=status.HTTP_200_OK)


    def post(self, request):
        fbo_id = request.data.get('fbo_id')
        airport_id = request.data.get('airport_id')
        action = request.data.get('action')

        if action == 'add':
            fbo_available_airport, created = AirportAvailableFbo.objects.get_or_create(
                fbo_id=fbo_id,
                airport_id=airport_id
            )

            fbo = fbo_available_airport.fbo

            data = {
                'id': fbo.id,
                'name': fbo.name
            }

            return Response(data, status=status.HTTP_200_OK)
        
        elif action == 'delete':
            AirportAvailableFbo.objects.filter(
                fbo_id=fbo_id,
                airport_id=airport_id
            ).delete()

            return Response(status=status.HTTP_200_OK)
