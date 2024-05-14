from rest_framework import (permissions, status)
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User

from api.models import (
    Airport,
    UserAvailableAirport,
    UserEmail
)

from api.serializers import UsersSerializer

class AirportAvailableUsersView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        airport = Airport.objects.get(pk=id)

        available_users = airport.available_users.filter(user__is_active=True).all()

        users = []

        for available_user in available_users:
            user = available_user.user

            emails = UserEmail.objects.filter(user=user)

            user.additional_emails = []

            if emails:
                email_array = []
                for email in emails:
                    obj = {
                        'id': email.id,
                        'email': email.email
                    }

                    email_array.append(obj)

                user.additional_emails = email_array

            users.append(user)

        vendor_names = []
        for user in users:
            if user.profile.vendor:
                vendor_names.append(user.profile.vendor.name)
            else:
                vendor_names.append('Livetakeoff')

        vendor_names = list(set(vendor_names))

        preferred_project_manager = airport.preferred_project_manager
        
        vendors = []
        for vendor_name in vendor_names:
            vendor = {
                'name': vendor_name,
                'users': []
            }

            for user in users:
                if user.profile.vendor:
                    if user.profile.vendor.name == vendor_name:
                        if preferred_project_manager:
                            if user == preferred_project_manager:
                                user.is_preferred_project_manager = True
                            else:
                                user.is_preferred_project_manager = False
                        else:
                            user.is_preferred_project_manager = False

                        serializer = UsersSerializer(user)

                        vendor['users'].append(serializer.data)
                else:
                    if vendor_name == 'Livetakeoff':
                        if preferred_project_manager:
                            if user == preferred_project_manager:
                                user.is_preferred_project_manager = True
                            else:
                                user.is_preferred_project_manager = False
                        else:
                            user.is_preferred_project_manager = False

                        serializer = UsersSerializer(user)

                        vendor['users'].append(serializer.data)

            vendors.append(vendor)

        return Response(vendors, status=status.HTTP_200_OK)
    
    def post(self, request):
        airport_id = request.data.get('airport_id')
        user_id = request.data.get('user_id')

        UserAvailableAirport.objects.create(
            airport_id=airport_id,
            user_id=user_id
        )

        return Response({'message': 'User available airport created'}, status=status.HTTP_200_OK)
    
    def patch(self, request):
        airport_id = request.data.get('airport_id')
        user_id = request.data.get('user_id')

        airport = Airport.objects.get(pk=airport_id)

        user = User.objects.get(pk=user_id)

        # toggle preferred project manager
        if airport.preferred_project_manager == user:
            airport.preferred_project_manager = None
        else:
            airport.preferred_project_manager = user

        airport.save(update_fields=['preferred_project_manager'])

        return Response({'message': 'Preferred project manager set'}, status=status.HTTP_200_OK)

