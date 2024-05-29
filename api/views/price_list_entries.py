from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from api.models import PriceListEntries

class DynamicDataPagination(PageNumberPagination):
    page_size = 200  

class PriceListEntriesView(APIView):
    pagination_class = DynamicDataPagination

    def get(self, request, *args, **kwargs):
        # Fetch PriceListEntries in the following format. It needs to be an array
        #aircraft_type.name  service.name   price_list_1.name  price_list_2.name  price_list_3.name  price_list_4.name    
        #aircraft_one        basic exterior 100                200                300                400 

        # Fetch all PriceListEntries
        price_list_entries = PriceListEntries.objects.all()

        # Create a array to store the data

        data = []

        # Loop through all the PriceListEntries
        for price_list_entry in price_list_entries:
            # Create a dictionary to store the data
            row = {
                'aircraft_type': price_list_entry.aircraft_type.name,
                'service': price_list_entry.service.name,
            }

            # Loop through all the price_list_entries
            for price_list_entry in price_list_entries:
                row[price_list_entry.price_list.name] = price_list_entry.price

            # Append the row to the data array
            data.append(row)

        paginator = self.pagination_class()
        page = paginator.paginate_queryset(data, request, view=self)
        if page is not None:
            return paginator.get_paginated_response(page)

        return Response(data, status=status.HTTP_200_OK)