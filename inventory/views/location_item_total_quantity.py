from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from inventory.models import (
    LocationItem,
)

class LocationItemTotalQuantityView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        item_name = self.request.data.get('searchText', '')
        location_id = self.request.data.get('location', None)
        measure_by_id = self.request.data.get('measureById', None)
        area_id = self.request.data.get('areaId', None)
        item_status = self.request.data.get('status', None)
        threshold_met = self.request.data.get('thresholdMet', False)
        minimum_required_met = self.request.data.get('minimumRequiredMet', None)
        out_of_stock_met = self.request.data.get('outOfStockMet', None)

        # Count the total quantity of items in LocationItem table taking into consideration the filters
        # search by item name contains
        qs = LocationItem.objects \
                        .filter(item__name__icontains=item_name, item__active=True) \
                        .prefetch_related('location', 'item') \
                        .order_by('item__name')
        
        if location_id:
            # only fetch the items that are present in LocationItem table
            qs = qs.filter(location_id=location_id)

            if item_status:
                qs = qs.filter(status=item_status)

            if threshold_met:
                # within a specific location_item, if the location_item.quantity is less than the location_item.threshold, then include it in the queryset
                # the comparison needs to be for each location item, you cannot compare to just any threshold
                qs = qs.filter(location_id=location_id, quantity__lte=F('threshold'), quantity__gt=0)

            if minimum_required_met:
                qs = qs.filter(location_id=location_id, quantity__lte=F('minimum_required'), quantity__gt=0)

            if out_of_stock_met:
                qs = qs.filter(location_id=location_id, quantity=0)
            
        if measure_by_id:
            qs = qs.filter(item__measure_by=measure_by_id)

        if area_id:
            qs = qs.filter(item__area=area_id)
        
        total_quantity = qs.aggregate(total_quantity=Sum('quantity'))['total_quantity']

        return Response({'totalQuantity': total_quantity}, status=status.HTTP_200_OK)
