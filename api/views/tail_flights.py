from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from datetime import datetime
from zoneinfo import ZoneInfo

from api.flightaware_api_service import FlightawareApiService

from ..models import (
        Job,
        TailIdent
    )

class TailFlightsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        job = get_object_or_404(Job, pk=id)

        enable_flightaware_tracking = job.enable_flightaware_tracking
        arrival_date = job.estimatedETA
        tail_number = job.tailNumber

        if not enable_flightaware_tracking:
            return Response({'error': 'FlightAware tracking is not enabled for this job'}, status=status.HTTP_400_BAD_REQUEST)
        
        if arrival_date is None:
            return Response({'error': 'The estimated arrival date is not set for this job'}, status=status.HTTP_400_BAD_REQUEST)

        # Only proceed if the job.status is either:  ('A', 'Accepted'), ('S', 'Assigned'), ('U', 'Submitted'), ('W', 'WIP'),
        if job.status not in ['A', 'S', 'U', 'W']:
            return Response({'error': 'The job status is not in the correct state to track flights'}, status=status.HTTP_400_BAD_REQUEST)

        tail_ident = TailIdent.objects.filter(tail_number=tail_number).first()

        if tail_ident is None:
            return Response({'error': 'No ident found for the tail number'}, status=status.HTTP_400_BAD_REQUEST)
        
        ident = tail_ident.ident

        # arrival_date must be in the following format as a string: 'YYYY-MM-DD'
        arrival_date = arrival_date.strftime('%Y-%m-%d')

        response = FlightawareApiService().get_flight_info(ident, arrival_date)

        flights = []

        if response:
            flights = response.get('flights', [])

            #iterate through flights and convert he following values with this format: 2025-01-30T16:14:15Z to just 16:14
            # the values to convert are: scheduled_out, estimated_out, scheduled_on, estimated_on
            # these values can be null, so check if they are not null before converting
            # Use the timezone field specified in origin and destination as follows:
            # scheduled_off and estimated_off should be converted to the timezone of the origin
            # scheduled_on and estimated_on should be converted to the timezone of the destination
            for flight in flights:
                origin_timezone = flight.get('origin', {}).get('timezone')
                destination_timezone = flight.get('destination', {}).get('timezone')

                if flight.get('scheduled_off'):
                    # convert the value to the timezone of the origin
                    # Convert string to datetime object
                    utc_dt = datetime.strptime(flight.get('scheduled_off'), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=ZoneInfo("UTC"))

                    # Convert to provided origin timezone
                    timezoned_scheduled_off = utc_dt.astimezone(ZoneInfo(origin_timezone))

                    local_scheduled_off = timezoned_scheduled_off.strftime("%H:%M")

                    flight['local_scheduled_off'] = local_scheduled_off + " LT"

                if flight.get('estimated_off'):
                    # convert the value to the timezone of the origin
                    # Convert string to datetime object
                    utc_dt = datetime.strptime(flight.get('estimated_off'), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=ZoneInfo("UTC"))

                    # Convert to provided origin timezone
                    timezoned_estimated_off = utc_dt.astimezone(ZoneInfo(origin_timezone))

                    local_estimated_off = timezoned_estimated_off.strftime("%H:%M")

                    flight['local_estimated_off'] = local_estimated_off + " LT"

                if flight.get('scheduled_on'):
                    # convert the value to the timezone of the destination
                    # Convert string to datetime object
                    utc_dt = datetime.strptime(flight.get('scheduled_on'), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=ZoneInfo("UTC"))

                    # Convert to provided destination timezone
                    timezoned_scheduled_on = utc_dt.astimezone(ZoneInfo(destination_timezone))

                    local_scheduled_on = timezoned_scheduled_on.strftime("%H:%M")

                    flight['local_scheduled_on'] = local_scheduled_on + " LT"

                if flight.get('estimated_on'):
                    # convert the value to the timezone of the destination
                    # Convert string to datetime object
                    utc_dt = datetime.strptime(flight.get('estimated_on'), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=ZoneInfo("UTC"))

                    # Convert to provided destination timezone
                    timezoned_estimated_on = utc_dt.astimezone(ZoneInfo(destination_timezone))

                    local_estimated_on = timezoned_estimated_on.strftime("%H:%M")

                    flight['local_estimated_on'] = local_estimated_on + " LT"

        return Response(flights, status=status.HTTP_200_OK)