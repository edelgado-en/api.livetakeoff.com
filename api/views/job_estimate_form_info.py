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
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        """
        Get all the data needed to create a new job estimate.
        """
        if not self.can_create_estimate(request.user):
            return Response({'error': 'You do not have permission to create a job estimate'}, status=status.HTTP_403_FORBIDDEN)

        aircraft_types = AircraftType.objects.filter(active=True).all().order_by('name')
        
        airports = Airport.objects.filter(active=True).all().order_by('name')
        
        fbos = FBO.objects.filter(active=True).all().order_by('name')

        # only get public services
        services = Service.objects.filter(public=True, active=True).all().order_by('name')


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
        

        if not aircraft_type_dtos:
            return Response({'error': 'No aircraft types found'}, status=status.HTTP_404_NOT_FOUND)

        if not airport_dtos:
            return Response({'error': 'No airports found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not fbo_dtos:
            return Response({'error': 'No fbos found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not service_dtos:
            return Response({'error': 'No services found'}, status=status.HTTP_404_NOT_FOUND)

        response = {
            'aircraft_types': aircraft_type_dtos,
            'airports': airport_dtos,
            'fbos': fbo_dtos,
            'services': service_dtos,
        }

        return Response(response, status.HTTP_200_OK)


    def can_create_estimate(self, user):
        """
        Only customer users can create estimates.
        """

        user_profile = UserProfile.objects.get(user=user)
        
        if user_profile and user_profile.customer is not None:
            return True

        
        return False