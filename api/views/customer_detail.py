from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from ..serializers import (
     CustomerDetailSerializer,
     )

from ..models import (
        Customer,
        CustomerSettings,
        UserProfile
    )


class CustomerDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        # customer = get_object_or_404(Customer, pk=id)
        customer = Customer.objects.select_related('contact').get(pk=id)
        
        try:
            settings = CustomerSettings.objects.get(customer=customer)
            customer.settings = settings

            if not self.can_view_customer(request.user, customer):
                return Response({'error': 'You do not have permission to view this customer'}, status=status.HTTP_403_FORBIDDEN)

            serializer = CustomerDetailSerializer(customer)
            
            return Response(serializer.data)

        except CustomerSettings.DoesNotExist:
            return Response({'error': 'Customer settings not found'}, status=status.HTTP_404_NOT_FOUND)



    def can_view_customer(self, user, customer):
        if user.is_superuser \
          or user.is_staff \
          or user.groups.filter(name='Account Managers').exists():
           return True

        user_profile = UserProfile.objects.select_related('customer').get(user=user)

        # customer user can only see its own customer
        if user_profile.customer.id == customer.id:
            return True

        return False