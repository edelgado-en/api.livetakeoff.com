from django.db.models import Q
from rest_framework import (permissions, status)

from ..serializers import (AirportSerializer)
from rest_framework.generics import ListCreateAPIView
from ..models import (Airport)


class AirportsView(ListCreateAPIView):
    queryset = Airport.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AirportSerializer