from django.db.models import Q
from rest_framework import (permissions, status)

from inventory.serializers import (LocationSerializer)
from rest_framework.generics import ListAPIView
from inventory.models import (Location, LocationUser)


class LocationsView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = LocationSerializer

    def get_queryset(self):
        name = self.request.data.get('name', '')
        active = self.request.data.get('active', True)

        user = self.request.user

        qs = Location.objects \
                       .filter(name__icontains=name, active=active) \
                       .order_by('name')
        
        if user.groups.filter(name='Project Managers').exists():
            # only get the locations specify in LocationUser
            qs = qs.filter(location_user__user=user)

        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)