from django.db.models import Q, F
from rest_framework import (permissions,status)
from rest_framework .response import Response
from rest_framework.generics import ListAPIView
from inventory.serializers import (
    LocationItemActivitySerializer,
)

from api.pagination import CustomPageNumberPagination

from inventory.models import (
    LocationItemActivity
)

class LocationItemActivityListView(ListAPIView):
    serializer_class = LocationItemActivitySerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        item_id = self.request.data.get('item_id')

        # fetch all location item activities where the location_item.item_id = item_id
        qs = LocationItemActivity.objects \
                                    .filter(location_item__item_id=item_id) \
                                    .order_by('-timestamp')
        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)