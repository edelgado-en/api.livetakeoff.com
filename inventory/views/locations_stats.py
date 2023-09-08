from django.db.models import F, Count
from rest_framework import (permissions, status)

from rest_framework.response import Response
from rest_framework.views import APIView
from inventory.models import (LocationItem)

class LocationsStatsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def post(self, request):
        out_of_stock = self.request.data.get('outOfStock', False)
        low_stock = self.request.data.get('lowStock', False)

        if out_of_stock:
            # query the LocationItems table and count the entries where quantity = 0.
            # But the resultset should just be a list of location names where each name is unique. Do not repeat the location names.
            # the result set should also include the actual number of items that are out of stock for each location name
            # the result set must be sorted by highest number of out of stock items
            # The result set should look like this: [{'name': 'location name', 'quantity_out_of_stock': 5}, {'name': 'location name', 'quantity_out_of_stock': 3}]
            qs = LocationItem.objects \
                            .filter(quantity=0, on_hold=False) \
                            .values('location__name', 'location__id') \
                            .annotate(count=Count('location__name')) \
                            .order_by('-count')
        
        elif low_stock:
            # query the LocationItems table and count the entries where quantity <= minimum_required.
            # But the resultset should just be a list of location names where each name is unique. Do not repeat the location names.
            # the result set should also include the actual number of items that are out of stock for each location name
            # the result set must be sorted by highest number of out of stock items
            # The result set should look like this: [{'name': 'location name', 'quantity_out_of_stock': 5}, {'name': 'location name', 'quantity_out_of_stock': 3}]
            qs = LocationItem.objects \
                            .filter(minimum_required__isnull=False, quantity__lte=F('minimum_required'), quantity__gt=0, minimum_required__gt=1) \
                            .values('location__name', 'location__id') \
                            .annotate(count=Count('location__name')) \
                            .order_by('-count')
            
        
        # iterate through qs and return an array of dictionaries. Each entry should name name, and count
        # the result set should look like this: [{'name': 'location name', 'count': 5}, {'name': 'location name', 'count': 3}]
        result = []
        for item in qs:
            result.append({'id': item['location__id'], 'name': item['location__name'], 'count': item['count']})
        
        return Response(result, status=status.HTTP_200_OK)
            

            