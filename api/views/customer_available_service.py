from rest_framework import (permissions, status)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import (
    CustomerService,
    Customer
)

class CustomerAvailableServiceView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        customer = Customer.objects.get(pk=id)
        customer_available_services = customer.services.all()

        # return an array of airports with id, initials, and name
        data = []
        for customer_available_service in customer_available_services:
            service = customer_available_service.service
            data.append({
                'id': service.id,
                'name': service.name
            })

        return Response(data, status=status.HTTP_200_OK)


    def post(self, request):
        customer_id = request.data.get('customer_id')
        service_id = request.data.get('service_id')
        action = request.data.get('action')

        if action == 'add':
            customer_available_service, created = CustomerService.objects.get_or_create(
                customer_id=customer_id,
                service_id=service_id
            )

            service = customer_available_service.service

            data = {
                'id': service.id,
                'name': service.name
            }

            return Response(data, status=status.HTTP_200_OK)
        
        elif action == 'delete':
            CustomerService.objects.filter(
                customer_id=customer_id,
                service_id=service_id
            ).delete()

            return Response(status=status.HTTP_200_OK)
