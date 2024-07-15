from django.db.models import Q, F
from rest_framework import (permissions,status)
from rest_framework .response import Response
from rest_framework.generics import ListAPIView
from inventory.serializers import (
        LocationItemDetailSerializer,
    )

from api.pagination import CustomPageNumberPagination
from inventory.models import (
        LocationItem
    )

class LocationItemsListView(ListAPIView):
    serializer_class = LocationItemDetailSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        item_name = self.request.data.get('searchText', '')
        location_id = self.request.data.get('location', None)
        measure_by_id = self.request.data.get('measureById', None)
        area_id = self.request.data.get('areaId', None)
        status = self.request.data.get('status', None)
        threshold_met = self.request.data.get('thresholdMet', False)
        minimum_required_met = self.request.data.get('minimumRequiredMet', None)
        out_of_stock_met = self.request.data.get('outOfStockMet', None)
        on_hold = self.request.data.get('onHold', None)
        in_stock = self.request.data.get('inStock', None)

        # search by item name contains
        qs = LocationItem.objects \
                        .filter(item__name__icontains=item_name, item__active=True) \
                        .prefetch_related('location', 'item') \
                        .order_by('item__name')
        
        if location_id:
            # only fetch the items that are present in LocationItem table
            qs = qs.filter(location_id=location_id)

            if status:
                qs = qs.filter(status=status)

            if threshold_met:
                # within a specific location_item, if the location_item.quantity is less than the location_item.threshold, then include it in the queryset
                # the comparison needs to be for each location item, you cannot compare to just any threshold
                qs = qs.filter(location_id=location_id, quantity__lte=F('threshold'), quantity__gt=0)

            if minimum_required_met:
                qs = qs.filter(location_id=location_id, quantity__lte=F('minimum_required'), quantity__gt=0)

            if out_of_stock_met:
                qs = qs.filter(location_id=location_id, quantity=0, on_hold=False)

            if in_stock:
                qs = qs.filter(location_id=location_id, quantity__gt=0)

        if measure_by_id:
            qs = qs.filter(item__measure_by=measure_by_id)
        
        if area_id:
            qs = qs.filter(item__area=area_id)

        if on_hold:
            qs = qs.filter(on_hold=on_hold)

        return qs

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)