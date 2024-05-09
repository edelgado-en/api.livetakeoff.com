from django.db.models import Q
from rest_framework import (permissions, status)

from ..serializers import (AirportSerializer)
from rest_framework.generics import ListAPIView
from ..models import (Airport, UserAvailableAirport)


class AirportsView(ListAPIView):
    queryset = Airport.objects.all()
    
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AirportSerializer


    def get_queryset(self):
        name = self.request.data.get('name', '')
        open_jobs = self.request.data.get('open_jobs', False)
        closed_jobs = self.request.data.get('closed_jobs', False)

        qs = Airport.objects \
                       .filter(name__icontains=name, active=True) \
                       .order_by('name')

        # if open_jobs include only airports with open jobs. An open job is a job with status 'A' or 'U', or 'S' or 'W'
        if open_jobs:
            if self.request.user.profile.customer:
                qs = qs.filter(jobs__status__in=['A', 'U', 'S', 'W'], jobs__customer=self.request.user.profile.customer).distinct()
            else:
                qs = qs.filter(jobs__status__in=['A', 'U', 'S', 'W']).distinct()

        if closed_jobs:
            # if customer user, do not include T status
            if self.request.user.profile.customer:
                qs = qs.filter(jobs__status__in=['C', 'I'], jobs__customer=self.request.user.profile.customer).distinct()
            else:
                qs = qs.filter(jobs__status__in=['C', 'I', 'T']).distinct()

        if self.request.user.groups.filter(name='Internal Coordinators').exists() \
          or self.request.user.groups.filter(name='Project Managers').exists():
            user_airports = UserAvailableAirport.objects.filter(user=self.request.user).all()

            if user_airports:
                airport_ids = []
                for user_airport in user_airports:
                    airport_ids.append(user_airport.airport.id)

                qs = qs.filter(id__in=airport_ids)

        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)