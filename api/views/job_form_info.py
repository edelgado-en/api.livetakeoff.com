from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from ..models import (
        Customer,
        AircraftType,
        Airport,
        FBO,
        Service,
        RetainerService   
)

class JobFormInfoView(APIView):
    """
    View to gather all the data needed to create a new job.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        """
        Get all the data needed to create a new job.
        """
        if not self.can_create_job(request.user):
            return Response({'error': 'You do not have permission to create a job'}, status=status.HTTP_403_FORBIDDEN)

        customers = Customer.objects.all().order_by('name')
        aircraft_types = AircraftType.objects.all().order_by('name')
        airports = Airport.objects.all().order_by('name')
        fbos = FBO.objects.all().order_by('name')
        services = Service.objects.all().order_by('name')
        retainer_services = RetainerService.objects.all().order_by('name')

        customer_dtos = []
        for customer in customers:
            c = {
                'id': customer.id,
                'name': customer.name,
            }

            customer_dtos.append(c)

        aircraft_type_dtos = []
        for aircraft_type in aircraft_types:
            a = {
                'id': aircraft_type.id,
                'name': aircraft_type.name,
            }

            aircraft_type_dtos.append(a)

        airport_dtos = []
        for airport in airports:
            a = {
                'id': airport.id,
                'name': airport.name,
            }

            airport_dtos.append(a)

        fbo_dtos = []
        for fbo in fbos:
            f = {
                'id': fbo.id,
                'name': fbo.name,
            }

            fbo_dtos.append(f)
        
        service_dtos = []
        for service in services:
            s = {
                'id': service.id,
                'name': service.name,
            }

            service_dtos.append(s)
        
        retainer_service_dtos = []
        for retainer_service in retainer_services:
            r = {
                'id': retainer_service.id,
                'name': retainer_service.name,
            }

            retainer_service_dtos.append(r)
        
        if not customer_dtos:
            return Response({'error': 'No customers found'}, status=status.HTTP_404_NOT_FOUND)

        if not aircraft_type_dtos:
            return Response({'error': 'No aircraft types found'}, status=status.HTTP_404_NOT_FOUND)

        if not airport_dtos:
            return Response({'error': 'No airports found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not fbo_dtos:
            return Response({'error': 'No fbos found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not service_dtos:
            return Response({'error': 'No services found'}, status=status.HTTP_404_NOT_FOUND)

        response = {
            'customers': customer_dtos,
            'aircraft_types': aircraft_type_dtos,
            'airports': airport_dtos,
            'fbos': fbo_dtos,
            'services': service_dtos,
            'retainer_services': retainer_service_dtos,
        }

        return Response(response, status.HTTP_200_OK)


    def can_create_job(self, user):
        """
        Check if the user has permission to create a job.
        """
        if user.is_superuser or user.is_staff or user.groups.filter(name='Account Managers').exists():
            return True
        else:
            return False