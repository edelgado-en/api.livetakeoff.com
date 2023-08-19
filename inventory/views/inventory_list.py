from django.db.models import Q, F
from rest_framework import (permissions,status)
from rest_framework .response import Response
from rest_framework.generics import ListAPIView
from inventory.serializers import (
        ItemSerializer,
    )

from api.pagination import CustomPageNumberPagination
from inventory.models import (
        Item,
        LocationItem
    )

class InventoryListView(ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        name = self.request.data.get('searchText', '')
        location_id = self.request.data.get('location', None)
        measure_by_id = self.request.data.get('measureById', None)
        area_id = self.request.data.get('areaId', None)
        status = self.request.data.get('status', None)
        threshold_met = self.request.data.get('thresholdMet', False)
        minimum_required_met = self.request.data.get('minimumRequiredMet', None)

        # search by item name contains
        qs = Item.objects \
                        .filter(name__icontains=name, active=True) \
                        .prefetch_related('location_items') \
                        .order_by('name')
        
        if location_id:
            # only fetch the items that are present in LocationItem table
            qs = qs.filter(location_items__location_id=location_id)

            if status:
                qs = qs.filter(location_items__status=status)

            if threshold_met:
                # within a specific location_item, if the location_item.quantity is less than the location_item.threshold, then include it in the queryset
                # the comparison needs to be for each location item, you cannot compare to just any threshold
                qs = qs.filter(location_items__location_id=location_id, location_items__quantity__lte=F('location_items__threshold'))

            if minimum_required_met:
                qs = qs.filter(location_items__location_id=location_id, location_items__quantity__lte=F('location_items__minimum_required'))

                

        if measure_by_id:
            qs = qs.filter(measure_by=measure_by_id)

        if area_id:
            qs = qs.filter(area=area_id)

        return qs



    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)