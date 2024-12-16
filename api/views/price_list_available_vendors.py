from rest_framework import (permissions, status)
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import (
    VendorCustomerPriceList,
    PriceList,
    Vendor
)

class PriceListAvailableVendorsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        price_list_id = request.data.get('price_list_id')
        customer_id = request.data.get('customer_id')
        vendor_id = request.data.get('vendor_id')
        action = request.data.get('action', 'add')

        price_list = PriceList.objects.get(pk=price_list_id)

        if action == 'add':
            # return an error if VendorCustomerPriceList already exists
            if price_list.vendor_customer_price_lists.filter(customer_id=customer_id, vendor_id=vendor_id).exists():
                return Response({'error': 'VendorCustomerPriceList already exists'}, status=status.HTTP_400_BAD_REQUEST)

            vendor = Vendor.objects.get(pk=vendor_id)
            vendor_customer_price_list = VendorCustomerPriceList.objects.create(
                price_list=price_list,
                customer_id=customer_id,
                vendor=vendor
            )

            data = {
                'id': vendor_customer_price_list.id,
                'vendor': vendor.name
            }

            return Response(data, status=status.HTTP_200_OK)

        elif action == 'delete':
            vendor_customer_price_list = price_list.vendor_customer_price_lists.get(customer_id=customer_id, vendor_id=vendor_id).delete()

            return Response(status=status.HTTP_200_OK)
        
        elif action == 'fetch':
            # fetch all vendors for the given price list and customer
            vendor_customer_price_list = price_list.vendor_customer_price_lists.filter(customer_id=customer_id)

            data = []

            for mapping in vendor_customer_price_list:
                vendor = mapping.vendor

                # ensure that the vendor is unique
                if any(d['id'] == vendor.id for d in data):
                    continue

                data.append({
                    'id': vendor.id,
                    'name': vendor.name
                })

            return Response(data, status=status.HTTP_200_OK)