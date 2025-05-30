from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from datetime import datetime
from zoneinfo import ZoneInfo

from api.flightaware_api_service import FlightawareApiService

from api.models import (ServiceActivity, Customer)

class TailExteriorLevel2CheckerView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        tail_number = request.data.get('tail_number', None)
        ident = request.data.get('ident', None)
        customer_id = request.data.get('customer_id', None)

        # 1. Check if customer has a value for exterior_service_checker bigger than 0. If not, then return an object with a boolean value false for show_recommendation
        customer = get_object_or_404(Customer, pk=customer_id)
        if customer.exterior_service_checker <= 0:
            return Response({'show_recommendation': False}, status=status.HTTP_200_OK)
        
        # 2. Look in ServiceActivity for the LAST entry with status C for a service with flag is_exterior_detail_level_2 set as true
        last_exterior_service_activity = ServiceActivity.objects.filter(
            Q(service__is_exterior_detail_level_2=True) & 
            Q(job__tailNumber=tail_number) & 
            Q(job__customer=customer) &
            Q(status='C') 
        ).order_by('-timestamp').first()

        response = None

        ident_to_use = ident if ident else tail_number
        last_date = None

        if last_exterior_service_activity is not None:
            last_service_date = last_exterior_service_activity.timestamp

            # if last_service_date was completed less than 10 days ago, then use the last_service_date to get the flight info 
            if (datetime.now(ZoneInfo("UTC")) - last_service_date).days < 10:
                # last_service_date needs to be in the following format as a string: 'MM/DD/YY HH:MM LT'
                last_service_date = last_service_date.strftime("%m/%d/%y %H:%M LT")  # Formatting as MM/DD/YY HH:MM LT
                parsed_date = datetime.strptime(last_service_date, "%m/%d/%y %H:%M LT")  # Parsing the string
            
                # arrival_date must be in the following format as a string: 'YYYY-MM-DD'
                last_date = parsed_date.strftime("%Y-%m-%d")  # Formatting as YYYY-MM-DD

        response = FlightawareApiService().get_flight_info(ident_to_use, last_date)

        show_recommendation = False
        exterior_service_checker = customer.exterior_service_checker
        arrived_flights_count = 0

        if response:
            flights = response.get('flights', [])

            # iterate throught flights array and count how many entries have status 'Arrived'. If that number is equal or bigger than the exterior_service_checker, then set show_recommendation to true, and also return the number of arrived flights
            arrived_flights_count = sum(1 for flight in flights if flight.get('status') == 'Arrived')
            if arrived_flights_count >= exterior_service_checker:
                show_recommendation = True


        return Response({
            'show_recommendation': show_recommendation,
            'arrived_flights_count': arrived_flights_count
        }, status=status.HTTP_200_OK)
        