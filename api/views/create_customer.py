import json
from decimal import Decimal
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from api.models import (
        Customer,
        CustomerSettings,
        CustomerAdditionalFee,
        CustomerDiscount,
        CustomerDiscountService,
        CustomerDiscountAirport,
        CustomerAdditionalFeeAirport,
        CustomerAdditionalFeeFBO
    )

class CreateCustomerView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        if not self.can_create_customer(request.user):
            return Response({'error': 'You do not have permission to create a customer'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data

        # all values are optional except for name

        name = data.get('name')
        billingAddress = data.get('billingAddress')
        emailAddress = data.get('emailAddress')
        logo = data.get('logo')
        banner = data.get('coverPhoto')
        # you cannot a contact because you need to create the customer first
        #contact_id = data.get('contactId')
        
        about = data.get('about')
        billingInfo = data.get('billingInfo')
        phone_number = data.get('phone_number')
        retainer_amount = data.get('retainerAmount')
        price_list_id = data.get('priceListId')
        special_instructions = data.get('specialInstructions')
        showSpendingInfo = data.get('showSpendingInfo')
        allowCancelJob = data.get('allowCancelJob')
        showJobPrice = data.get('showJobPrice')
        discounts = data.get('discounts')
        fees = data.get('fees')

        if retainer_amount == '':
            retainer_amount = None
        else:
            retainer_amount = Decimal(retainer_amount.replace(',','.'))

        if showSpendingInfo == 'true':
            showSpendingInfo = True
        else:
            showSpendingInfo = False

        if allowCancelJob == 'true':
            allowCancelJob = True
        else:
            allowCancelJob = False

        if showJobPrice == 'true':
            showJobPrice = True
        else:
            showJobPrice = False


        customer = Customer(
            name=name,
            billingAddress=billingAddress,
            emailAddress=emailAddress,
            logo=logo,
            banner=banner,
            about=about,
            billingInfo=billingInfo,
            phone_number=phone_number
        )

        #if contact_id:
        #    customer.contact_id = contact_id

        customer.save()


        customer_settings = CustomerSettings(
                customer=customer,
                retainer_amount=retainer_amount,
                price_list_id=price_list_id,
                special_instructions=special_instructions,
                show_spending_info=showSpendingInfo,
                allow_cancel_job=allowCancelJob,
                show_job_price=showJobPrice
            )

        customer_settings.save()


        if discounts:
            discounts = json.loads(discounts)
            for discount in discounts:
                type_id = discount.get('type').get('id') 
                customer_discount = CustomerDiscount(
                                        customer_setting=customer_settings,
                                        discount=discount.get('discount'),
                                        percentage=discount.get('is_percentage'),
                                        type=type_id
                                    )

                customer_discount.save()

                if type_id == 'S':
                    for service in discount.get('services'):
                        customer_discount_service = CustomerDiscountService(customer_discount=customer_discount,
                                                                            service_id=service['id'])

                        customer_discount_service.save()


                if type_id == 'A':
                    for airport in discount.get('airports'):
                        customer_discount_airport = CustomerDiscountAirport(customer_discount=customer_discount,
                                                                            airport_id=airport['id'])

                        customer_discount_airport.save()



        if fees:
            fees = json.loads(fees)
            for fee in fees:
                type_id = fee.get('type').get('id') 

                customer_fee = CustomerAdditionalFee.objects.create(
                                customer_setting=customer_settings,
                                type=type_id,
                                fee=fee.get('fee'),
                                percentage=fee.get('is_percentage')
                            )

                if type_id == 'A':
                    for airport in fee.get('airports'):
                        CustomerAdditionalFeeAirport.objects.create(
                            customer_additional_fee=customer_fee,
                            airport_id=airport['id']
                        )

                if type_id == 'F':
                    for fbo in fee.get('fbos'):
                        CustomerAdditionalFeeFBO.objects.create(
                            customer_additional_fee=customer_fee,
                            fbo_id=fbo['id']
                        )


        return Response({'id': customer.id}, status=status.HTTP_201_CREATED)


    def can_create_customer(self, user):
        """
        Check if the user has permission to create a customer.
        """
        if user.is_superuser or user.is_staff or user.groups.filter(name='Account Managers').exists():
            return True
        else:
            return False