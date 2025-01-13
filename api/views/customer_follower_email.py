from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.models import (
        Customer,
        CustomerFollowerEmail
    )

class CustomerFollowerEmailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, id):
        customer = get_object_or_404(Customer, pk=id)
        email = request.data.get('email')
        action = request.data.get('action', 'add')

        if action == 'add' and email == '':
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        if action == 'add':
            if CustomerFollowerEmail.objects.filter(email=email, customer=customer).exists():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
            p = CustomerFollowerEmail(customer=customer, email=email)

            p.save()

            return Response(status=status.HTTP_201_CREATED)

        if action == 'delete':
            p = CustomerFollowerEmail.objects.get(email=email, customer=customer)

            p.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)
