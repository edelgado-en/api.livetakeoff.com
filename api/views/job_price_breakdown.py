from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from api.pricebreakdown_service import PriceBreakdownService

from api.models import (Job,
                        InvoicedService,
                        InvoicedDiscount,
                        VendorCustomerPriceList,
                        UserCustomer,
                        InvoicedFee)

class JobPriceBreakdownView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, id):
        job = Job.objects.prefetch_related('job_service_assignments') \
                         .select_related('customer__customer_settings__price_list') \
                         .get(pk=id)

        if not self.can_see_price_breakdown(request.user, job):
            return Response({'error': 'You do not have permission to see the price breakdown'}, status=status.HTTP_403_FORBIDDEN)
        
        invoiced_services = InvoicedService.objects.filter(job=job)

        if job.status == 'I' and invoiced_services.exists():
            aircraftType = job.aircraftType
            priceListType = job.invoiced_price_list

            invoice_fees = InvoicedFee.objects.filter(job=job)
            invoice_discounts = InvoicedDiscount.objects.filter(job=job)

            price_breakdown = {
                'priceListType': priceListType.name.upper(),
                'aircraftType': aircraftType.name,
                'services': [{'name': service.name, 'price': service.price} for service in invoiced_services],
                'servicesPrice': sum([service.price for service in invoiced_services]),
                'discounts': [{'name': discount.type,
                               'discount': discount.discount,
                               'isPercentage': discount.percentage,
                               'discount_dollar_amount': discount.discount_dollar_amount} for discount in invoice_discounts],
                'discountedPrice': job.discounted_price,
                'additionalFees': [{'name': fee.type,
                                    'fee': fee.fee,
                                    'isPercentage': fee.percentage,
                                    'additional_fee_dollar_amount': fee.fee_dollar_amount} for fee in invoice_fees],
                'totalPrice': job.price
            }

            price_breakdown['totalPrice'] = f"{price_breakdown['totalPrice']:,.2f}"

            return Response(price_breakdown, status=status.HTTP_200_OK)

        price_breakdown = {}

        if request.user.groups.filter(name='Project Managers').exists() \
            and not request.user.groups.filter(name='Internal Coordinators').exists():
            
            mapped_price_list = VendorCustomerPriceList.objects.filter(
                Q(vendor=job.vendor) & Q(customer=job.customer)
            ).first()

            if mapped_price_list:
                price_breakdown = PriceBreakdownService().get_price_breakdown(job, False, mapped_price_list.price_list)
            else:
                price_breakdown = PriceBreakdownService().get_price_breakdown(job, True)
        else:
            price_breakdown = PriceBreakdownService().get_price_breakdown(job)
        
        price_breakdown['totalPrice'] = f"{price_breakdown['totalPrice']:,.2f}"

        return Response(price_breakdown, status=status.HTTP_200_OK)

    def can_see_price_breakdown(self, user, job):

        if user.profile.customer and job.customer.customer_settings.show_job_price:
            if user.profile.customer == job.customer:
                return True

            # Get extra customers from UserCustomer for this user
            user_customers = UserCustomer.objects.filter(user=user).all()
            for user_customer in user_customers:
                if user_customer.customer == job.customer:
                    return True

        if user.is_superuser \
            or user.is_staff \
            or user.profile.show_job_price \
            or user.groups.filter(name='Account Managers').exists():
            return True

        return False