from rest_framework import (permissions, status)
from rest_framework .response import Response

from ..serializers import (AircraftTypeSerializer)
from rest_framework.generics import ListAPIView
from ..pagination import CustomPageNumberPagination
from api.models import (AircraftType)


class AircraftTypesView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = AircraftTypeSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        name = self.request.data['name']

        qs = AircraftType.objects \
                       .filter(name__icontains=name) \
                       .order_by('name')

        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)