from rest_framework import (permissions, status)
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import (
    UserAvailableAirport
)

class UserAvailableAirportsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, id):
        user = User.objects.get(pk=id)
        user_available_airports = user.available_airports.all()

        # return an array of airports with id, initials, and name
        data = []
        for user_available_airport in user_available_airports:
            airport = user_available_airport.airport
            data.append({
                'id': airport.id,
                'initials': airport.initials,
                'name': airport.name
            })


        return Response(data, status=status.HTTP_200_OK)


    def post(self, request):
        user_id = request.data.get('user_id')
        airport_id = request.data.get('airport_id')

        user_available_airport, created = UserAvailableAirport.objects.get_or_create(
            user_id=user_id,
            airport_id=airport_id
        )

        airport = user_available_airport.airport

        data = {
            'id': airport.id,
            'initials': airport.initials,
            'name': airport.name
        }

        return Response(data, status=status.HTTP_200_OK)
        


    def delete(self, request):
        user_id = request.data.get('user_id')
        airport_id = request.data.get('airport_id')

        # delete an entry in the UserAvailableAirport table if it exists
        UserAvailableAirport.objects.filter(
            user_id=user_id,
            airport_id=airport_id
        ).delete()

        return Response(status=status.HTTP_200_OK)
