from rest_framework import (permissions, status)

from ..serializers import (RetainerServiceSerializer)
from rest_framework.generics import ListCreateAPIView
from api.models import (RetainerService)


class RetainerServicesView(ListCreateAPIView):
    queryset = RetainerService.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = RetainerServiceSerializer