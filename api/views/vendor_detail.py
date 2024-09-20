from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from ..serializers import (
     VendorDetailSerializer,
     )

from ..models import (
        Vendor,
    )

class VendorDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        if not self.can_view_customer(request.user):
            return Response({'error': 'You do not have permission to view this vendor'}, status=status.HTTP_403_FORBIDDEN)
        
        vendor = Vendor.objects.get(pk=id)

        serializer = VendorDetailSerializer(vendor)
        
        return Response(serializer.data)


    def patch(self, request, id):
        vendor = Vendor.objects.get(pk=id)

        if not self.can_view_customer(request.user):
            return Response({'error': 'You do not have permission to edit this vendor'}, status=status.HTTP_403_FORBIDDEN)


        name = request.data.get('name')
        phoneNumbers = request.data.get('phoneNumbers')
        billingAddress = request.data.get('billingAddress')
        emails = request.data.get('emails')
        notes = request.data.get('notes')
        active = request.data.get('active')

        vendor.name = name
        vendor.billing_address = billingAddress
        vendor.emails = emails
        vendor.phone_numbers = phoneNumbers
        vendor.notes = notes

        if active is not None:
            vendor.active = active

        vendor.save()

        return Response(status=status.HTTP_200_OK)


    def can_view_customer(self, user):
        if user.is_superuser \
          or user.is_staff \
          or user.groups.filter(name='Account Managers').exists():
           return True

        return False