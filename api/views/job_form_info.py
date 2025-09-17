from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from ..models import (
        Customer,
        AircraftType,
        Airport,
        FBO,
        Service,
        RetainerService,
        UserProfile,
        Tag,
        UserCustomer,
        UserAvailableAirport,
        Vendor
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

        user_profile = UserProfile.objects.get(user=request.user)

        if self.request.user.groups.filter(name='Internal Coordinators').exists():

            if not user_profile.enable_all_customers:
                user_customers = UserCustomer.objects.filter(user=self.request.user).all()

                if user_customers:
                    customer_ids = []
                    for user_customer in user_customers:
                        customer_ids.append(user_customer.customer.id)

                    customers = customers.filter(id__in=customer_ids)


        aircraft_types = AircraftType.objects.all().order_by('name')
        tags = Tag.objects.all().order_by('name')

        tags = tags.exclude(name='Scheduled')

        vendors = Vendor.objects.all().order_by('name')
        
        airports = Airport.objects.all().order_by('name')

        if self.request.user.groups.filter(name='Internal Coordinators').exists():

            if not user_profile.enable_all_airports:
                user_airports = UserAvailableAirport.objects.filter(user=self.request.user).all()

                if user_airports:
                    airport_ids = []
                    for user_airport in user_airports:
                        airport_ids.append(user_airport.airport.id)

                    airports = airports.filter(id__in=airport_ids)
        
        
        fbos = FBO.objects.all().order_by('name')

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
                'hours_of_operation': fbo.hours_of_operation,
            }

            fbo_dtos.append(f)
        
        tag_dtos = []
        for tag in tags:
            t = {
                'id': tag.id,
                'name': tag.name,
                'description': tag.description,
            }

            tag_dtos.append(t)
        
        vendor_dtos = []
        for vendor in vendors:
            v = {
                'id': vendor.id,
                'name': vendor.name,
            }

            vendor_dtos.append(v)

        if not customer_dtos:
            return Response({'error': 'No customers found'}, status=status.HTTP_404_NOT_FOUND)

        if not aircraft_type_dtos:
            return Response({'error': 'No aircraft types found'}, status=status.HTTP_404_NOT_FOUND)

        if not airport_dtos:
            return Response({'error': 'No airports found'}, status=status.HTTP_404_NOT_FOUND)
        
        if not fbo_dtos:
            return Response({'error': 'No fbos found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the user is a customer and get the customer id
       
        is_customer = user_profile and user_profile.customer is not None

        customer_id = None

        is_enable_request_priority = False
        hide_addons_services = False

        if is_customer:
            customer_id = user_profile.customer.id
            is_enable_request_priority = user_profile.customer.customer_settings.enable_request_priority
            hide_addons_services = user_profile.customer.customer_settings.hide_addons_services

        response = {
            'customers': customer_dtos,
            'aircraft_types': aircraft_type_dtos,
            'airports': airport_dtos,
            'fbos': fbo_dtos,
            'tags': tag_dtos,
            'customer_id': customer_id,
            'is_enable_request_priority': is_enable_request_priority,
            'hide_addons_services': hide_addons_services,
            'vendors': vendor_dtos,
        }

        return Response(response, status.HTTP_200_OK)


    def can_create_job(self, user):
        """
        Check if the user has permission to create a job.
        """

        user_profile = UserProfile.objects.get(user=user)
        is_customer = user_profile and user_profile.customer is not None

        if user.is_superuser \
                 or user.is_staff \
                 or is_customer \
                 or user.groups.filter(name='Account Managers').exists() \
                 or user.groups.filter(name='Internal Coordinators').exists():
            return True
        else:
            return False