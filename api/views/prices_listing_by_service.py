from django.db.models import Q
from decimal import Decimal
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from api.models import (PriceList, PriceListEntries, AircraftType, Service, Job)

class PricesListingByServiceView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        service_id = self.request.data.get('service_id')
        price_list_ids = self.request.data.get('price_list_ids', [])
        
        service = Service.objects.get(pk=service_id)
        # get the prices for each service for the provided service for all price lists
        price_list_entries = PriceListEntries.objects \
            .select_related('price_list') \
            .select_related('aircraft_type') \
            .filter(service=service) \
            .order_by('price_list__id', 'aircraft_type__id')

        # get all the aircraft types
        aircraft_types = AircraftType.objects.all().order_by('id')

        # get all the price lists for the provided price_list_ids
        price_lists = PriceList.objects.filter(id__in=price_list_ids)

        # price_lists has to be in the same order as price_list_ids
        price_lists = sorted(price_lists, key=lambda price_list: price_list_ids.index(price_list.id))

        # create the dictionary
        price_list_entries_dict = {}

        for aircraft_type in aircraft_types:
            price_list_entries_dict[aircraft_type.name] = {}
            for price_list in price_lists:
                price_list_entries_dict[aircraft_type.name][price_list.name] = Decimal('0.00')

        # populate the dictionary with the prices
        for price_list_entry in price_list_entries:
            price_list_entries_dict[price_list_entry.aircraft_type.name][price_list_entry.price_list.name] = price_list_entry.price


        # instead of a dictionary, return an array of services and in each entry an array of price list entries by price list
        # the array will look like this:
        # [
        #   {
        #     "aircraft_type": "Aircraft 1",
        #     "price_list_entries": [
        #       {
        #         "price_list": "Price List 1",
        #         "price": 100.00
        #       },
        #       {
        #         "price_list": "Price List 2",
        #         "price": 150.00
        #       }
        #     ]
        #   },
        #   {
        #     "aircraft_type": "Aircraft 2",
        #     "price_list_entries": [
        #       {
        #         "price_list": "Price List 1",
        #         "price": 200.00
        #       },
        #       {
        #         "price_list": "Price List 2",
        #         "price": 250.00
        #       }
        #     ]
        #   },
        #   {
        #     "aircraft_type": "Aircraft 3",
        #     "price_list_entries": [
        #       {
        #         "price_list": "Price List 1",
        #         "price": 300.00
        #       },
        #       {
        #         "price_list": "Price List 2",
        #         "price": 350.00
        #       }
        #     ]
        #   }
        # ]


        # create the array
        price_list_entries_array = []

        # if there is no price list entry, it should have a zero price
        for aircraft_type in aircraft_types:
            price_list_entries_array.append({
                "aircraft_type": aircraft_type.name,
                "price_list_entries": []
            })
            for price_list in price_lists:
                price_list_entries_array[-1]["price_list_entries"].append({
                    "price_list": price_list.name,
                    "price_list_id": price_list.id,
                    "price": price_list_entries_dict[aircraft_type.name][price_list.name]
                })
    

        return Response(price_list_entries_array, status.HTTP_200_OK)
            

