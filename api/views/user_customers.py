from rest_framework import (permissions, status)
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import (
    UserCustomer
)

class UserCustomersView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, id):
        user = User.objects.get(pk=id)
        user_customers = user.user_customers.all()

        data = []
        for user_customer in user_customers:
            customer = user_customer.customer
            data.append({
                'id': customer.id,
                'name': customer.name
            })
        
        return Response(data, status=status.HTTP_200_OK)
    

    def post(self, request):
        user_id = request.data.get('user_id')
        customer_id = request.data.get('customer_id')
        action = request.data.get('action')

        if action == 'add':
            user_customer, created = UserCustomer.objects.get_or_create(
                user_id=user_id,
                customer_id=customer_id
            )

            customer = user_customer.customer

            data = {
                'id': customer.id,
                'name': customer.name
            }

            return Response(data, status=status.HTTP_200_OK)
        
        elif action == 'delete':
            UserCustomer.objects.filter(
                user_id=user_id,
                customer_id=customer_id
            ).delete()

            return Response(status=status.HTTP_200_OK)