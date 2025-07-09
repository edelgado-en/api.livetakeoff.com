from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from zoneinfo import ZoneInfo
from datetime import datetime, timedelta
import time
import threading

from api.models import (CustomerTail, Customer, TailIdent, ServiceActivity, TailAircraftLookup)
from api.serializers import (
    CustomerTailSerializer,
)

from api.email_notification_service import EmailNotificationService
from api.flightaware_api_service import FlightawareApiService

class FlightBasedCleaningUpdateView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        thread = threading.Thread(target=self.flight_based_cleaning_update)
        thread.start()

        return Response({"message": "Flight based cleaning update started."}, status=status.HTTP_200_OK)
    
    def flight_based_cleaning_update(self):
        # This is the number of flights that must be arrived for level 1 cleaning to be recommended
        SERVICE_LEVEL_1_THRESHOLD = 10  
        
        # This is the number of flights that must be arrived for level 2 cleaning to be recommended
        SERVICE_LEVEL_2_THRESHOLD = 20  

        # Fetch all customers with enable_flight_based_scheduled_cleaning set to True
        customers = Customer.objects.filter(customer_settings__enable_flight_based_scheduled_cleaning=True)

        for customer in customers:
            active_tails = CustomerTail.objects.filter(customer=customer, is_active=True)

            tails_to_report = []

            for tail in active_tails:
                tail_ident = TailIdent.objects.filter(tail_number=tail.tail_number).first()
                ident_to_use = tail_ident.ident if tail_ident else tail.tail_number

                flights_response = FlightawareApiService().get_flight_info(ident_to_use, None)

                # Add a 2 seconds delay to avoid hitting the API rate limit
                time.sleep(2)

                if flights_response is None:
                    continue

                flights = flights_response.get('flights', [])

                is_exterior_level_1_due_for_cleaning = False
                is_exterior_level_2_due_for_cleaning = False
                is_interior_level_1_due_for_cleaning = False
                is_interior_level_2_due_for_cleaning = False

                # EXTERIOR LEVEL 2 CHECKER
                #########################################################################

                last_exterior_level_2_service_activity = ServiceActivity.objects.filter(
                    Q(service__is_exterior_detail_level_2=True) & 
                    Q(job__tailNumber=tail.tail_number) & 
                    Q(job__customer=customer) &
                    Q(status='C') 
                ).order_by('-timestamp').first()

                flights_count_since_last_exterior_level_2 = 0

                if last_exterior_level_2_service_activity:
                    last_service_date = last_exterior_level_2_service_activity.timestamp

                    for flight in flights:
                        if flight.get("status") == "Arrived":
                            scheduled_on_str = flight.get("scheduled_on")
                            if scheduled_on_str:
                                scheduled_on = datetime.fromisoformat(scheduled_on_str.replace("Z", "+00:00"))
                                if scheduled_on > last_service_date:
                                    flights_count_since_last_exterior_level_2 += 1
                    
                    if flights_count_since_last_exterior_level_2 >= SERVICE_LEVEL_2_THRESHOLD:
                        is_exterior_level_2_due_for_cleaning = True

                    #update customer tail model
                    tail.last_exterior_level_2_service_date = last_service_date
                    tail.last_exterior_level_2_location = last_exterior_level_2_service_activity.job.airport.initials

                # END EXTERIOR LEVEL 2 CHECKER
                #########################################################################

                # EXTERIOR LEVEL 1 CHECKER
                #########################################################################

                last_exterior_level_1_service_activity = ServiceActivity.objects.filter(
                    Q(service__is_exterior_detail_level_1=True) & 
                    Q(job__tailNumber=tail.tail_number) & 
                    Q(job__customer=customer) &
                    Q(status='C') 
                ).order_by('-timestamp').first()

                flights_count_since_last_exterior_level_1 = 0

                if last_exterior_level_1_service_activity:
                    last_service_date = last_exterior_level_1_service_activity.timestamp

                    for flight in flights:
                        if flight.get("status") == "Arrived":
                            scheduled_on_str = flight.get("scheduled_on")
                            if scheduled_on_str:
                                scheduled_on = datetime.fromisoformat(scheduled_on_str.replace("Z", "+00:00"))
                                if scheduled_on > last_service_date:
                                    flights_count_since_last_exterior_level_1 += 1

                    if flights_count_since_last_exterior_level_1 >= SERVICE_LEVEL_1_THRESHOLD \
                        and is_exterior_level_2_due_for_cleaning is False:
                        is_exterior_level_1_due_for_cleaning = True

                    # update customer tail model
                    tail.last_exterior_level_1_service_date = last_service_date
                    tail.last_exterior_level_1_location = last_exterior_level_1_service_activity.job.airport.initials

                # END EXTERIOR LEVEL 1 CHECKER
                #########################################################################

                # INTERIOR LEVEL 2 CHECKER
                #########################################################################
                last_interior_level_2_service_activity = ServiceActivity.objects.filter(
                    Q(service__is_interior_detail_level_2=True) & 
                    Q(job__tailNumber=tail.tail_number) & 
                    Q(job__customer=customer) &
                    Q(status='C') 
                ).order_by('-timestamp').first()

                flights_count_since_last_interior_level_2 = 0

                if last_interior_level_2_service_activity:
                    last_service_date = last_interior_level_2_service_activity.timestamp

                    for flight in flights:
                        if flight.get("status") == "Arrived":
                            scheduled_on_str = flight.get("scheduled_on")
                            if scheduled_on_str:
                                scheduled_on = datetime.fromisoformat(scheduled_on_str.replace("Z", "+00:00"))
                                if scheduled_on > last_service_date:
                                    flights_count_since_last_interior_level_2 += 1
                    
                    if flights_count_since_last_interior_level_2 >= SERVICE_LEVEL_2_THRESHOLD:
                        is_interior_level_2_due_for_cleaning = True

                    # update customer tail model
                    tail.last_interior_level_2_service_date = last_service_date
                    tail.last_interior_level_2_location = last_interior_level_2_service_activity.job.airport.initials

                # END INTERIOR LEVEL 2 CHECKER
                #########################################################################

                # INTERIOR LEVEL 1 CHECKER
                #########################################################################
                last_interior_level_1_service_activity = ServiceActivity.objects.filter(
                    Q(service__is_interior_detail_level_1=True) & 
                    Q(job__tailNumber=tail.tail_number) & 
                    Q(job__customer=customer) &
                    Q(status='C') 
                ).order_by('-timestamp').first()

                flights_count_since_last_interior_level_1 = 0

                if last_interior_level_1_service_activity:
                    last_service_date = last_interior_level_1_service_activity.timestamp

                    for flight in flights:
                        if flight.get("status") == "Arrived":
                            scheduled_on_str = flight.get("scheduled_on")
                            if scheduled_on_str:
                                scheduled_on = datetime.fromisoformat(scheduled_on_str.replace("Z", "+00:00"))
                                if scheduled_on > last_service_date:
                                    flights_count_since_last_interior_level_1 += 1

                    if flights_count_since_last_interior_level_1 >= SERVICE_LEVEL_1_THRESHOLD \
                        and is_interior_level_2_due_for_cleaning is False:
                        is_interior_level_1_due_for_cleaning = True


                    # update customer tail model
                    tail.last_interior_level_1_service_date = last_service_date
                    tail.last_interior_level_1_location = last_interior_level_1_service_activity.job.airport.initials

                # END INTERIOR LEVEL 1 CHECKER
                #########################################################################

                # update customer tail model with due cleanings
                tail.is_exterior_level_1_service_due = is_exterior_level_1_due_for_cleaning
                tail.is_exterior_level_2_service_due = is_exterior_level_2_due_for_cleaning
                tail.is_interior_level_1_service_due = is_interior_level_1_due_for_cleaning
                tail.is_interior_level_2_service_due = is_interior_level_2_due_for_cleaning

                #update customer tail model with flights count since last service
                tail.flights_since_last_exterior_level_1_service = flights_count_since_last_exterior_level_1
                tail.flights_since_last_exterior_level_2_service = flights_count_since_last_exterior_level_2
                tail.flights_since_last_interior_level_1_service = flights_count_since_last_interior_level_1
                tail.flights_since_last_interior_level_2_service = flights_count_since_last_interior_level_2

                # get aircraft type name from TailAircraftLookup
                aircraft_lookup = TailAircraftLookup.objects.filter(tail_number=tail.tail_number).first()
                aircraft_type_name = aircraft_lookup.aircraft_type.name if aircraft_lookup else "Unknown"

                tail.aircraft_type_name = aircraft_type_name

                are_services_due = False

                # an entry is only added if at least one of the is_*_due_for_cleaning is True
                if (is_exterior_level_1_due_for_cleaning or is_exterior_level_2_due_for_cleaning or
                    is_interior_level_1_due_for_cleaning or is_interior_level_2_due_for_cleaning):
                    
                    are_services_due = True
                    
                    tail_report = {
                        "tail_number": tail.tail_number,
                        "aircraft_type": aircraft_type_name,
                        "since_last_exterior_level_1": f"{flights_count_since_last_exterior_level_1} flights",
                        "since_last_exterior_level_2": f"{flights_count_since_last_exterior_level_2} flights",
                        "since_last_interior_level_1": f"{flights_count_since_last_interior_level_1} flights",
                        "since_last_interior_level_2": f"{flights_count_since_last_interior_level_2} flights"
                    }

                    if is_exterior_level_1_due_for_cleaning:
                        tail_report["since_last_exterior_level_1"] += ". DUE"
                    
                    if is_exterior_level_2_due_for_cleaning:
                        tail_report["since_last_exterior_level_2"] += ". DUE"

                    if is_interior_level_1_due_for_cleaning:
                        tail_report["since_last_interior_level_1"] += ". DUE"

                    if is_interior_level_2_due_for_cleaning:
                        tail_report["since_last_interior_level_2"] += ". DUE"

                    tails_to_report.append(tail_report)

                # Get the date for 2 days ago
                two_days_ago = datetime.now(ZoneInfo("UTC")) - timedelta(days=2)
                flight_history_found = False

                for flight in flights:
                    if flight.get("status") == "Arrived":
                        scheduled_on_str = flight.get("scheduled_on")
                        if scheduled_on_str:
                            scheduled_on = datetime.fromisoformat(scheduled_on_str.replace("Z", "+00:00"))
                            if scheduled_on > two_days_ago:
                                flight_history_found = True
                                break

                # Determine tail status
                if flight_history_found is False:
                    tail.status = 'N'
                elif are_services_due:
                    tail.status = 'S'
                else:
                    tail.status = 'O'

                # save the tail with the updated information
                tail.save()
            
            # If tails_to_report is not empty, then send an email to the customer with the report
            if len(tails_to_report) > 0:
                EmailNotificationService().send_flight_based_scheduled_cleaning_notification(customer.name, tails_to_report)