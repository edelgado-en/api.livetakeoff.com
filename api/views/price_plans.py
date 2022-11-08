from decimal import Decimal
from django.db.models import Count
from rest_framework import (permissions, status)
from rest_framework .response import Response

from api.serializers import PriceListSerializer
from rest_framework.generics import ListCreateAPIView
from api.models import (PriceList, PriceListEntries, Customer, CustomerSettings)


class PricePlansView(ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = PriceListSerializer

    def get_queryset(self):
        # count how many customers are using each price list
        # and add that to the queryset
        return PriceList.objects.annotate(
            num_customers=Count('customer_settings')).order_by('id')


    def delete(self, request, *args, **kwargs):
        price_list_id = self.kwargs.get('id')
        price_list = PriceList.objects.get(pk=price_list_id)
        standard_price_list = PriceList.objects.get(name='Standard')

        # update all customers using this price list to use the standard price list
        CustomerSettings.objects.filter(price_list=price_list).update(price_list=standard_price_list)

        # all the PriceListEntries for the given price list id need to be deleted
        PriceListEntries.objects.filter(price_list_id=price_list_id).delete()

        # delete the price list with the given id
        PriceList.objects.get(pk=price_list_id).delete()


        return Response(status=status.HTTP_204_NO_CONTENT)



    def create(self, request, *args, **kwargs):
        user = self.request.user

        name = self.request.data.get('name')
        description = self.request.data.get('description')
        price_list_id = self.request.data.get('price_list_id')
        operator = self.request.data.get('operator')
        percentage = self.request.data.get('percentage')

        if percentage:
            percentage = Decimal(percentage)
        else:
            percentage = 0.0


        # create a new price list with the given name and description and set the prices for all services with the given operator and percentage
        # for all aircrafts. A price is determine based on aircraft type and service
        new_price_list = PriceList.objects.create(name=name, description=description, created_by=request.user)

        # copy all of the prices from the provided price list into the new one, and adjust the price based on the operator and percentage
        for price_list_entry in PriceListEntries.objects \
                                                .select_related('aircraft_type') \
                                                .select_related('service') \
                                                .filter(price_list_id=price_list_id):
            price = price_list_entry.price
            if operator == 'add':
                # add the percentage to the price
                price = price + (price * percentage / 100)

            elif operator == 'subtract':
                # subtract the percentage from the price
                price = price - (price * percentage / 100)


            PriceListEntries.objects.create(price_list=new_price_list,
                                            aircraft_type=price_list_entry.aircraft_type,
                                            service=price_list_entry.service,
                                            price=price)


        return Response({'id': new_price_list.id}, status=status.HTTP_201_CREATED)

