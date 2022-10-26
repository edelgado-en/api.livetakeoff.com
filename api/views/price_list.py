from rest_framework import (permissions, status)

from api.serializers import PriceListSerializer
from rest_framework.generics import ListCreateAPIView
from api.models import (PriceList)


class PriceListView(ListCreateAPIView):
    queryset = PriceList.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PriceListSerializer