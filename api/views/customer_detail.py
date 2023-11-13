from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.template.loader import get_template

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



    def patch(self, request, id):
        customer = Customer.objects.get(pk=id)
        settings = CustomerSettings.objects.get(customer=customer)

        if not self.can_view_customer(request.user, customer):
            return Response({'error': 'You do not have permission to edit this customer'}, status=status.HTTP_403_FORBIDDEN)


        name = request.data.get('name')
        about = request.data.get('about')
        phoneNumber = request.data.get('phoneNumber')
        billingAddress = request.data.get('billingAddress')
        emailAddress = request.data.get('emailAddress')
        billingInfo = request.data.get('billingInfo')
        specialInstructions = request.data.get('specialInstructions')
        priceListId = request.data.get('priceListId')
        retainerAmount = request.data.get('retainerAmount')

        # update customer
        customer.name = name
        customer.billingAddress = billingAddress
        customer.emailAddress = emailAddress
        customer.about = about
        customer.billingInfo = billingInfo
        customer.phone_number = phoneNumber

        customer.save()

        # update customer settings
        settings.special_instructions = specialInstructions
        settings.price_list_id = priceListId

        # if retainerAmount is empty string, don't set it
        if retainerAmount == '':
            settings.retainer_amount = None
        else:
            settings.retainer_amount = retainerAmount

        settings.save()


        return Response(status=status.HTTP_200_OK)


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