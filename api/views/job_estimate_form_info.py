from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from ..models import (
        Customer,
        AircraftType,
        Airport,
        FBO,
        Service,
        UserProfile   
)


class JobEstimateFormInfoView(APIView):
    """
    View to gather all the data needed to create a new job estimate.
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        """
        Get all the data needed to create a new job estimate.
        """
        

        customers = Customer.objects.all().order_by('name')

        aircraft_types = AircraftType.objects.filter(active=True).all().order_by('name')

        if request.user.profile.customer:
            airports = Airport.objects.filter(public=True, active=True).order_by('name')
            fbos = FBO.objects.filter(public=True, active=True).order_by('name')
            services = Service.objects.filter(public=True, active=True).order_by('name')
        else:
            airports = Airport.objects.filter(active=True).all().order_by('name')
            fbos = FBO.objects.filter(active=True).all().order_by('name')
            services = Service.objects.filter(active=True).all().order_by('name')

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
                'category': service.category,
            }

            service_dtos.append(s)
        

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
        }

        return Response(response, status.HTTP_200_OK)
