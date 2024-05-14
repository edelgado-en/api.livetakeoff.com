from rest_framework import (permissions, status)
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User

from api.models import (
    UserAvailableAirport,
)

class RemoveAirportAvailableUsersView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        airport_id = request.data.get('airport_id')
        user_id = request.data.get('user_id')

        UserAvailableAirport.objects.filter(user_id=user_id, airport_id=airport_id).delete()

        return Response(status=status.HTTP_200_OK)