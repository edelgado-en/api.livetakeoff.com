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


import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from api.email_util import EmailUtil


class CustomerDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        """ subject = 'This is my subject'
        tailNumber = 'NEJ123'
        body = f'<img src="https://res.cloudinary.com/datidxeqm/image/upload/v1655812995/npcjg9zhd7j4kdfbbpce.jpg" alt=""/><div style="color:\'red\'">Tailnumber: {tailNumber}</div>'

        email_util = EmailUtil()
        email_util.send_email('enriquedelgado806@gmail.com',
                              subject,
                              body) """

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