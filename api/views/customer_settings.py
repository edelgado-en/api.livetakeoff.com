from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.models import CustomerSettings

from api.serializers import CustomerSettingsSerializer


class CustomerSettingsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def patch(self, request, id):
        if not self.can_update_customer_settings(request.user):
            return Response({'error': 'You do not have permission to update customer settings'},
                             status=status.HTTP_403_FORBIDDEN)

        customer_setting = get_object_or_404(CustomerSettings, pk=id)

        serializer = CustomerSettingsSerializer(customer_setting, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    # Settings can only be changed by admins and account managers
    def can_update_customer_settings(self, user):
        if user.is_superuser \
          or user.is_staff \
          or user.groups.filter(name='Account Managers').exists():
           return True

        return False;