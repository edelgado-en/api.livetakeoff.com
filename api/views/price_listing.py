from django.db.models import Q
from decimal import Decimal
from django.db.models import Count
from rest_framework import (permissions, status)
from rest_framework .response import Response

from api.serializers import PriceListSerializer
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView
from api.models import (PriceList, PriceListEntries, AircraftType, Service, Job)

from ..pricebreakdown_service import PriceBreakdownService

class PriceListingView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, id):
        aircraft_type = AircraftType.objects.get(pk=id)
        # get the prices for each service for the provided aircraft type for all price lists
        price_list_entries = PriceListEntries.objects \
            .select_related('price_list') \
            .select_related('service') \
            .filter(aircraft_type=aircraft_type) \
            .order_by('price_list__id', 'service__id')

        # create a dictionary of price lists and their prices for each service
        # the dictionary will look like this:
        # {
        #    1: {
        #       1: 100.00,
        #       2: 200.00,
        #       3: 300.00
        #   },
        #    2: {
        #       1: 150.00,
        #       2: 250.00,
        #       3: 350.00
        #   }
        # }
        # where the first key is the price list id and the second key is the service id
        # and the value is the price
        # the dictionary will be used to create a table of prices for each service for each price list
        # the table will look like this:
        # +----------------+--------+--------+--------+
        # | Price List     | Service 1 | Service 2 | Service 3 |
        # +----------------+--------+--------+--------+
        # | Price List 1   | 100.00 | 200.00 | 300.00 |
        # | Price List 2   | 150.00 | 250.00 | 350.00 |
        # +----------------+--------+--------+--------+
        # where the first column is the price list name and the other columns are the prices for each service
        # the first row is the service names
        # the first column is the price list names
        # the other columns are the prices for each service
          
        # if a service is not included in the price list entries, then you have to set it in the dictionary with a zero price
        # for example, if the price list entries only have prices for service 1 and service 2, then the dictionary will look like this:
        # {
        #   1: {
        #      1: 100.00,
        #     2: 200.00,
        #    3: 0.00
        # },
        #  2: {
        #    1: 150.00,
        #   2: 250.00,
        # 3: 0.00
        # }
        # }
        # where the first key is the price list id and the second key is the service id
        # and the value is the price
        # the dictionary will be used to create a table of prices for each service for each price list
        # the table will look like this:
        # +----------------+--------+--------+--------+
        # | Price List     | Service 1 | Service 2 | Service 3 |
        # +----------------+--------+--------+--------+
        # | Price List 1   | 100.00 | 200.00 | 0.00 |
        # | Price List 2   | 150.00 | 250.00 | 0.00 |
        # +----------------+--------+--------+--------+
        # where the first column is the price list name and the other columns are the prices for each service
        # the first row is the service names
        # the first column is the price list names
        # the other columns are the prices for each service

        # get all the services
        services = Service.objects.all().order_by('id')

        # get all the price lists
        price_lists = PriceList.objects.all().order_by('id')

        # create the dictionary
        price_list_entries_dict = {}

        
        for service in services:
            price_list_entries_dict[service.name] = {}
            for price_list in price_lists:
                price_list_entries_dict[service.name][price_list.name] = Decimal('0.00')

        # populate the dictionary with the prices
        for price_list_entry in price_list_entries:
            price_list_entries_dict[price_list_entry.service.name][price_list_entry.price_list.name] = price_list_entry.price


        # instead of a dictionary, return an array of services and in each entry an array of price list entries by price list
        # the array will look like this:
        # [
        #   {
        #     "service": "Service 1",
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
        #     "service": "Service 2",
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
        #     "service": "Service 3",
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
        # where the first entry is the service name and the price list entries are the prices for each price list
        # the price list entries are an array of price list entries
        # each price list entry is the price list name and the price

        # create the array
        price_list_entries_array = []

        # if there is no price list entry, it should have a zero price
        for service in services:
            price_list_entries_array.append({
                "service": service.name,
                "price_list_entries": []
            })
            for price_list in price_lists:
                price_list_entries_array[-1]["price_list_entries"].append({
                    "price_list": price_list.name,
                    "price": price_list_entries_dict[service.name][price_list.name]
                })
    


        return Response(price_list_entries_array, status.HTTP_200_OK)


    def post(self, request, id):

        price_list_name = self.request.data.get('name')
        price_list_entries = self.request.data.get('price_list_entries') # service name, price
        aircraft_type_id = self.request.data.get('aircraft_type_id')

        # get price list by name
        price_list = PriceList.objects.get(name=price_list_name)

        # update the prices in PriceListEntries for the provided price list with the list of services and prices
        for price_list_entry in price_list_entries:
            service_name = price_list_entry.get('service')
            price = price_list_entry.get('price')
            
            service = Service.objects.get(name=service_name)

            # if the price list entry does not exist, create a new one
            try:
                price_list_entry = PriceListEntries.objects.get(price_list=price_list, service=service, aircraft_type_id=aircraft_type_id)
                price_list_entry.price = price
                price_list_entry.save()

            except PriceListEntries.DoesNotExist:
                price_list_entry = PriceListEntries(price_list=price_list,
                                                    service=service,
                                                    aircraft_type_id=aircraft_type_id,
                                                    price=price)
                price_list_entry.save()


        # update the price for all jobs with customer using a customer setting with the price list and aircraft type with is_auto_priced as true
        # get all the jobs with customer using a customer setting with the price list and aircraft type with is_auto_priced as true
        # not invoiced
        jobs = Job.objects.filter(Q(customer__customer_settings__price_list=price_list) & 
                                  Q(aircraftType_id=aircraft_type_id) &
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
            

