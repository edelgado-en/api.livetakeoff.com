from django.db.models import Q
from decimal import Decimal
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from api.models import (PriceList, PriceListEntries, AircraftType, Service, Job)

from ..pricebreakdown_service import PriceBreakdownService

class PriceListingByServiceView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        aircraft_type = Service.objects.get(pk=id)
        # get the prices for each service for the provided service for all price lists
        price_list_entries = PriceListEntries.objects \
            .select_related('price_list') \
            .select_related('aircraft_type') \
            .filter(service=aircraft_type) \
            .order_by('price_list__id', 'aircraft_type__id')

        # get all the aircraft types
        aircraft_types = AircraftType.objects.all().order_by('id')

        # get all the price lists
        price_lists = PriceList.objects.all().order_by('id')

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
                    "price": price_list_entries_dict[aircraft_type.name][price_list.name]
                })
    

        return Response(price_list_entries_array, status.HTTP_200_OK)


    def post(self, request, id):
        price_list_name = self.request.data.get('name')
        price_list_entries = self.request.data.get('price_list_entries') # aircraft_type name, price
        service_id = self.request.data.get('service_id')

        # get price list by name
        price_list = PriceList.objects.get(name=price_list_name)

        # update the prices in PriceListEntries for the provided price list with the list of services and prices
        for price_list_entry in price_list_entries:
            aircraft_type_name = price_list_entry.get('aircraft_type')
            price = price_list_entry.get('price')
            
            aircraft_type = AircraftType.objects.get(name=aircraft_type_name)

            # if the price list entry does not exist, create a new one
            try:
                price_list_entry = PriceListEntries.objects.get(price_list=price_list,
                                                                aircraft_type=aircraft_type,
                                                                service_id=service_id)
                price_list_entry.price = price
                price_list_entry.save()

            except PriceListEntries.DoesNotExist:
                price_list_entry = PriceListEntries(price_list=price_list,
                                                    aircraft_type=aircraft_type,
                                                    service_id=service_id,
                                                    price=price)
                price_list_entry.save()


        # update the price for all jobs with customer using a customer setting with the price list and aircraft type with is_auto_priced as true
        # get all the jobs with customer using a customer setting with the price list and aircraft type with is_auto_priced as true
        # not invoiced
        jobs = Job.objects.filter(Q(customer__customer_settings__price_list=price_list) & 
                                  Q(aircraftType_id=service_id) &
                                  Q(is_auto_priced=True) &
                                  ~Q(status='I')
                                  )

        # update the price for each job using the PriceBreakdownService
        price_service = PriceBreakdownService()
        for job in jobs:
            price_breakdown = price_service.get_price_breakdown(job)
            job.price = price_breakdown.get('totalPrice')
            job.travel_fees_amount_applied = price_breakdown.get('total_travel_fees_amount_applied')
            job.fbo_fees_amount_applied = price_breakdown.get('total_fbo_fees_amount_applied')
            job.vendor_higher_price_amount_applied = price_breakdown.get('total_vendor_higher_price_amount_applied')
            job.management_fees_amount_applied = price_breakdown.get('total_management_fees_amount_applied')

            job.save()
        

        return Response(status=status.HTTP_200_OK)
            

