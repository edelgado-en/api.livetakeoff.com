from rest_framework import (permissions, status)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import (
    Airport,
    UserEmail
)

from api.serializers import UsersSerializer

class AirportAvailableUsersView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        airport = Airport.objects.get(pk=id)

        available_users = airport.available_users.all()

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

        vendors = []
        for vendor_name in vendor_names:
            vendor = {
                'name': vendor_name,
                'users': []
            }

            for user in users:
                if user.profile.vendor:
                    if user.profile.vendor.name == vendor_name:
                        serializer = UsersSerializer(user)
                        vendor['users'].append(serializer.data)
                else:
                    if vendor_name == 'Livetakeoff':
                        serializer = UsersSerializer(user)
                        vendor['users'].append(serializer.data)

            vendors.append(vendor)

        return Response(vendors, status=status.HTTP_200_OK)

