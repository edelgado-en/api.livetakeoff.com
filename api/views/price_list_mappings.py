from rest_framework import (permissions, status)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import (
    VendorCustomerPriceList,
    PriceList,
    Vendor
)

from api.serializers import (
    CustomerSerializer,
)

class PriceListMappingsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        price_list = PriceList.objects.get(pk=id)
        vendor_customer_price_list_mappings = price_list.vendor_customer_price_lists.all()

        # Get the total number of vendors
        total_vendors = Vendor.objects.count()

        data = []
        for mapping in vendor_customer_price_list_mappings:
            # add an object that looks like this: customer, number of vendors mapped to the customer
            customer = mapping.customer

            # the customer has to be unique. Do not repeat the customer in the data list
            if any(d['customer']['id'] == customer.id for d in data):
                continue

            customer_serializer = CustomerSerializer(customer)

            # count how many entries this customer have in the VendorCustomerPriceList table for this price_list
            vendor_count = price_list.vendor_customer_price_lists.filter(customer=customer).count()

            data.append({
                'id': mapping.id,
                'customer': customer_serializer.data,
                'vendor_count': f"{vendor_count} out of {total_vendors}"
            })
            

        return Response(data, status=status.HTTP_200_OK)


    def post(self, request):
        price_list_id = request.data.get('price_list_id')
        vendor_ids = request.data.get('vendor_ids')
        customer_id = request.data.get('customer_id')
        action = request.data.get('action', 'add')

        price_list = PriceList.objects.get(pk=price_list_id)

        if action == 'add':
            # there can only be one mapping for a price list customer
            # return an error if there is already a mapping for the customer
            if price_list.vendor_customer_price_lists.filter(customer_id=customer_id).exists():
                return Response({'error': 'A mapping already exists for the customer'}, status=status.HTTP_400_BAD_REQUEST)

            for vendor_id in vendor_ids:
                VendorCustomerPriceList.objects.create(
                    price_list=price_list,
                    vendor_id=vendor_id,
                    customer_id=customer_id
                )

        elif action == 'delete':
            # there can only be one mapping for a price list customer
            # return an error if there is already a mapping for the customer
            if not price_list.vendor_customer_price_lists.filter(customer_id=customer_id).exists():
                return Response({'error': 'No mapping exists for the customer'}, status=status.HTTP_400_BAD_REQUEST)

            # delete all the mappings for the customer
            price_list.vendor_customer_price_lists.filter(customer_id=customer_id).delete()

        return Response(status=status.HTTP_200_OK)
