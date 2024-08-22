from django.db.models import Q, F
from rest_framework import (permissions, status)

from ..serializers import (AirportSerializer)
from rest_framework.generics import ListAPIView
from ..models import (Airport, UserAvailableAirport)
from ..pagination import CustomPageNumberPagination

class AirportsView(ListAPIView):
    queryset = Airport.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AirportSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        name = self.request.data.get('name', '')
        open_jobs = self.request.data.get('open_jobs', False)
        closed_jobs = self.request.data.get('closed_jobs', False)
        sort_selected = self.request.data.get('sortSelected', None)

        qs = Airport.objects.filter(Q(name__icontains=name) | Q(initials__icontains=name), active=True)

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

        if sort_selected:
            # sort_selected can be either 'asc' or 'desc'
            # sort by airport.fee
            if sort_selected == 'asc':
                # nulls should be first, then order by fee asc
                qs = qs.order_by(F('fee').asc(nulls_first=True))

            elif sort_selected == 'desc':
                qs = qs.order_by(F('fee').desc(nulls_last=True))

        else:
            qs = qs.order_by('name')

        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)