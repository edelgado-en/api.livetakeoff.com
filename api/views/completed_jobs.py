from django.db.models import Q, Case, When, Value, CharField
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from ..pagination import CustomPageNumberPagination

from api.pricebreakdown_service import PriceBreakdownService

from api.models import (Job,
                        JobStatusActivity,
                        PriceListEntries,
                        ServiceActivity,
                        UserCustomer,
                        UserAvailableAirport,
                        InvoicedDiscount,
                        InvoicedFee,
                        InvoicedService,
                        UserCustomer
                        )

from ..serializers import (
        JobCompletedSerializer,
        JobAdminSerializer
    )


class CompletedJobsListView(ListAPIView):
    serializer_class = JobCompletedSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        searchText = self.request.data['searchText']
        status = self.request.data['status']
        airport = self.request.data.get('airport')
        fbo = self.request.data.get('fbo')
        customer = self.request.data.get('customer')
        additionalFees = self.request.data.get('additionalFees')

        requestedDateFrom = self.request.data.get('requestedDateFrom')
        requestedDateTo = self.request.data.get('requestedDateTo')

        arrivalDateFrom = self.request.data.get('arrivalDateFrom')
        arrivalDateTo = self.request.data.get('arrivalDateTo')

        departureDateFrom = self.request.data.get('departureDateFrom')
        departureDateTo = self.request.data.get('departureDateTo')

        completeByDateFrom = self.request.data.get('completeByDateFrom')
        completeByDateTo = self.request.data.get('completeByDateTo')

        completionDateFrom = self.request.data.get('completionDateFrom')
        completionDateTo = self.request.data.get('completionDateTo')

        qs = Job.objects.all()
        
        user_profile = self.request.user.profile
        
        for additionalFee in additionalFees:
            if additionalFee == 'A':
                qs = qs.filter(travel_fees_amount_applied__gt=0)
            elif additionalFee == 'F':
                qs = qs.filter(fbo_fees_amount_applied__gt=0)
            elif additionalFee == 'M':
                qs = qs.filter(management_fees_amount_applied__gt=0)
            elif additionalFee == 'V':
                qs = qs.filter(vendor_higher_price_amount_applied__gt=0)

        # if customer user, then only show jobs for that customer and extra customers
        if user_profile.customer:
            if user_profile.is_job_submitter_only:
                qs = qs.filter(created_by=self.request.user)
            
            if customer and customer != 'All':
                qs = qs.filter(customer_id=customer)
            else:
                user_customers = UserCustomer.objects.filter(user=self.request.user).all()

                customer_ids = []
                
                # append self.request.user.profile.customer.id to customer_ids
                customer_ids.append(self.request.user.profile.customer.id)

                if user_customers:
                    for user_customer in user_customers:
                        customer_ids.append(user_customer.customer.id)

                qs = qs.filter(customer_id__in=customer_ids)

        else:
            if customer and customer != 'All':
                qs = qs.filter(customer_id=customer)

        if self.request.user.groups.filter(name='Internal Coordinators').exists():
            
            if not user_profile.enable_all_customers:
                user_customers = UserCustomer.objects.filter(user=self.request.user).all()

                if user_customers:
                    customer_ids = []
                    for user_customer in user_customers:
                        customer_ids.append(user_customer.customer.id)

                    qs = qs.filter(customer_id__in=customer_ids)

            if not user_profile.enable_all_airports:
                user_available_airports = UserAvailableAirport.objects.filter(user=self.request.user).all()

                if user_available_airports:
                    airport_ids = []
                    for user_available_airport in user_available_airports:
                        airport_ids.append(user_available_airport.airport.id)

                    qs = qs.filter(airport_id__in=airport_ids)


        if searchText:
                qs = qs.filter(Q(tailNumber__icontains=searchText)
                               | Q(customer_purchase_order__icontains=searchText)
                               | Q(purchase_order__icontains=searchText)
                              )

        if status == 'All':
            # if customer user, do not include T status
            if self.request.user.profile.customer:
                qs = qs.filter(Q(status='C') | Q(status='I') | Q(status='A') | Q(status='S') | Q(status='U') | Q(status='W') | Q(status='N'))
            else:
                qs = qs.filter(Q(status='C') | Q(status='I') | Q(status='T') | Q(status='N'))

        else:
            qs = qs.filter(status=status)


        if airport and airport != 'All':
            qs = qs.filter(airport_id=airport)

        if fbo and fbo != 'All':
            qs = qs.filter(fbo_id=fbo)

        # apply date range filters
        if arrivalDateFrom:
            qs = qs.filter(estimatedETA__gte=arrivalDateFrom)

        if arrivalDateTo:
            qs = qs.filter(estimatedETA__lte=arrivalDateTo)

        if requestedDateFrom:
            qs = qs.filter(requestDate__gte=requestedDateFrom)

        if requestedDateTo:
            qs = qs.filter(requestDate__lte=requestedDateTo)

        if departureDateFrom:
            qs = qs.filter(estimatedETD__gte=departureDateFrom)

        if departureDateTo:
            qs = qs.filter(estimatedETD__lte=departureDateTo)

        if completeByDateFrom:
            qs = qs.filter(completeBy__gte=completeByDateFrom)

        if completeByDateTo:
            qs = qs.filter(completeBy__lte=completeByDateTo)

        if completionDateFrom:
            qs = qs.filter(completion_date__gte=completionDateFrom)
        
        if completionDateTo:
            qs = qs.filter(completion_date__lte=completionDateTo)

        # after applying all the filters, now prefetch to increase performance
        qs = qs.select_related('airport', 'customer', 'fbo', 'aircraftType')

        # the sorting needs to be by status in the following order:
        #('A', 'Accepted'),
        #('S', 'Assigned'),
        #('U', 'Submitted'),
        #('W', 'WIP'),
        #('C', 'Complete'),
        #('T', 'Cancelled'),
        #('R', 'Review'),
        #('I', 'Invoiced'),
        
        order = {
            'U': 1,
            'A': 2,
            'S': 3,
            'W': 4,
            'C': 5,
            'I': 6,
            'N': 7,
            'T': 8
        }

        ordering_conditions = [When(status=status, then=Value(order.get(status))) for status in order.keys()]

        secondary_ordering = '-completion_date'
        
        qs = qs.order_by(
                Case(*ordering_conditions, default=Value(8), output_field=CharField()),
                secondary_ordering
            )

        return qs



    def post(self, request, *args, **kwargs):
        """ if not self.can_see_completed_list(request.user):
            return Response({'error': 'You do not have permission to view completed jobs'}, status=status.HTTP_403_FORBIDDEN) """


        return self.list(request, *args, **kwargs)


    def patch(self, request, *args, **kwargs):
        """ if not self.can_see_completed_list(request.user):
            return Response({'error': 'You do not have permission to edit completed jobs'}, status=status.HTTP_403_FORBIDDEN) """

        job = get_object_or_404(Job, pk=kwargs['id'])

        serializer = JobAdminSerializer(job, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            new_status = request.data['status']

            if job.vendor:
                vendor_charge = job.vendor_charge if job.vendor_charge else 0
                vendor_additional_cost = job.vendor_additional_cost if job.vendor_additional_cost else 0
                job.subcontractor_profit = job.price - (vendor_charge + vendor_additional_cost)

                job.save(update_fields=['subcontractor_profit'])
            
            JobStatusActivity.objects.create(job=job, user=request.user, status=new_status)

            for service in job.job_service_assignments.all():
                service_price = 0
                customer_settings = job.customer.customer_settings
                aircraft_type = job.aircraftType
                service_id = service.service.id

                try:
                    price_list_entry = PriceListEntries.objects.get(
                                                    price_list_id=customer_settings.price_list_id,
                                                    aircraft_type_id=aircraft_type.id,
                                                    service_id=service_id)
                
                    service_price = price_list_entry.price

                    # Update ServiceActivity for the corresponding service_price with the service_price
                    service_activity = ServiceActivity.objects.filter(job=job, service_id=service_id, status='C').first()

                    if service_activity:
                        service_activity.price = service_price

                        service_activity.save(update_fields=['price'])

                except PriceListEntries.DoesNotExist:
                    continue

            price_breakdown = PriceBreakdownService().get_price_breakdown(job)

            InvoicedService.objects.filter(job=job).delete()
            InvoicedDiscount.objects.filter(job=job).delete()
            InvoicedFee.objects.filter(job=job).delete()

            job.invoiced_price_list = job.customer.customer_settings.price_list
            job.discounted_price = price_breakdown['discountedPriceNoFormat']

            job.save(update_fields=['invoiced_price_list', 'discounted_price'])

            for service in price_breakdown['services']:
                InvoicedService.objects.create(job=job, name=service['name'], price=service['price'])

            for discount in price_breakdown['discounts']:
                InvoicedDiscount.objects.create(job=job,
                                                type=discount['name'],
                                                discount=discount['discount'],
                                                discount_dollar_amount=discount['discount_dollar_amount'],
                                                percentage=discount['isPercentage'])
                
            for fee in price_breakdown['additionalFees']:
                InvoicedFee.objects.create(job=job,
                                        type=fee['name'],
                                        fee=fee['fee'],
                                        fee_dollar_amount=fee['additional_fee_dollar_amount'],
                                        percentage=fee['isPercentage']
                                        )
            
            return Response(serializer.data, status.HTTP_200_OK)
        
        return Response({'error': 'Missing Required Fields'}, status.HTTP_400_BAD_REQUEST)


    """ def can_see_completed_list(self, user):
        return not user.groups.filter(name='Project Managers').exists() """