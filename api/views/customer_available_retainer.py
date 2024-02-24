from rest_framework import (permissions, status)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import (
    CustomerRetainerService,
    Customer
)

class CustomerAvailableRetainerView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        customer = Customer.objects.get(pk=id)
        customer_available_retainers = customer.retainer_services.all()

        # return an array of airports with id, initials, and name
        data = []
        for customer_available_retainer in customer_available_retainers:
            retainer_service = customer_available_retainer.retainer_service
            data.append({
                'id': retainer_service.id,
                'name': retainer_service.name
            })

        return Response(data, status=status.HTTP_200_OK)


    def post(self, request):
        customer_id = request.data.get('customer_id')
        retainer_id = request.data.get('retainer_id')
        action = request.data.get('action')

        if action == 'add':
            customer_available_retainer, created = CustomerRetainerService.objects.get_or_create(
                customer_id=customer_id,
                retainer_service_id=retainer_id
            )

            retainer_service = customer_available_retainer.retainer_service

            data = {
                'id': retainer_service.id,
                'name': retainer_service.name
            }

            return Response(data, status=status.HTTP_200_OK)
        
        elif action == 'delete':
            CustomerRetainerService.objects.filter(
                customer_id=customer_id,
                retainer_service_id=retainer_id
            ).delete()

            return Response(status=status.HTTP_200_OK)
