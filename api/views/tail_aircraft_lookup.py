from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.models import (TailAircraftLookup, TailServiceLookup)


class TailAircraftLookupView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, tailnumber):
        
        try:
            lookup = TailAircraftLookup.objects \
                                       .select_related('aircraft_type') \
                                       .select_related('customer') \
                                       .get(tail_number=tailnumber)

            aircraft_type = lookup.aircraft_type

            # do a lookup by services as well. Return an array of services
            services = []
            try:
                lookup_services = TailServiceLookup.objects \
                                        .select_related('service') \
                                        .filter(tail_number=tailnumber) \
                                        .order_by('service__id')
            
                for service in lookup_services:
                    services.append({'id': service.service.id, 'name': service.service.name})

            except TailServiceLookup.DoesNotExist:
                pass


            return Response({
                'aircraft_id': aircraft_type.id,
                'aircraft_name': aircraft_type.name,
                'customer_id': lookup.customer.id,
                'customer_name': lookup.customer.name,
                'services': services
            }, status=status.HTTP_200_OK) 

        except TailAircraftLookup.DoesNotExist:
            return Response(None)

