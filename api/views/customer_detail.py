from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from ..serializers import (
     CustomerSerializer,
     )

from ..models import (
        Customer,
        UserProfile
    )


class CustomerDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        customer = get_object_or_404(Customer, pk=id)
        
        if not self.can_view_customer(request.user, customer):
            return Response({'error': 'You do not have permission to view this customer'}, status=status.HTTP_403_FORBIDDEN)


        # TODO: you need a full serializer to get all the stuff you need
        serializer = CustomerSerializer(customer)
        
        return Response(serializer.data)


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