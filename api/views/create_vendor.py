import json
from decimal import Decimal
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from api.models import (
        Vendor,
    )

class CreateVendorView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        if not self.can_create_vendor(request.user):
            return Response({'error': 'You do not have permission to create a customer'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data

        name = data.get('name')

        if Vendor.objects.filter(name=name).exists():
            return Response({'error': 'Vendor with this name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        notes = data.get('notes')
        billing_address = data.get('billingAddress')
        emails = data.get('emails')
        phone_numbers = data.get('phoneNumbers')
        logo = data.get('logo')
        
        vendor = Vendor(
            name=name,
            billing_address=billing_address,
            emails=emails,
            phone_numbers=phone_numbers,
            logo=logo,
            notes=notes,
        )

        vendor.save()

        return Response({'id': vendor.id}, status=status.HTTP_201_CREATED)


    def can_create_vendor(self, user):
        """
        Check if the user has permission to create a customer.
        """
        if user.is_superuser or user.is_staff or user.groups.filter(name='Account Managers').exists():
            return True
        else:
            return False