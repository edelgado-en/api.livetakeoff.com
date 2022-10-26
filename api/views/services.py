from rest_framework import (permissions, status)

from ..serializers import (ServiceSerializer)
from rest_framework.generics import ListCreateAPIView
from ..models import (Service)

class ServicesView(ListCreateAPIView):
    queryset = Service.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ServiceSerializer