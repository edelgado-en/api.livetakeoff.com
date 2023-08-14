from rest_framework import (permissions, status)
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView

from inventory.models import (
    LocationUser,
)

class LocationUserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        user = User.objects.get(pk=id)

        user_location_users = user.location_user.all()

        data = []
        for location_user in user_location_users:
            location = location_user.location
            data.append({
                'id': location.id,
                'name': location.name
            })

        return Response(data, status=status.HTTP_200_OK)
    

    def post(self, request, id):
        location_id = request.data.get('location_id')
        action = request.data.get('action')
        
        if action == 'add':
            user_location_user, created = LocationUser.objects.get_or_create(
                user_id=id,
                location_id=location_id
            )

            location = user_location_user.location

            data = {
                'id': location.id,
                'name': location.name
            }

            return Response(data, status=status.HTTP_200_OK)
        
        elif action == 'delete':
            LocationUser.objects.filter(
                user_id=id,
                location_id=location_id
            ).delete()

            return Response(status=status.HTTP_200_OK)