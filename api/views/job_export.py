import csv
from django.http import HttpResponse
from rest_framework.views import APIView
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import ListAPIView
from ..pagination import CustomPageNumberPagination
from api.models import Job
from ..serializers import (
        JobCompletedSerializer,
        JobAdminSerializer
    )


class JobExportCSVView(APIView):
    serializer_class = JobAdminSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        if not self.can_export(request.user):
            return Response({'error': 'You do not have permission to export jobs'}, status=status.HTTP_403_FORBIDDEN)


        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'
        writer = csv.DictWriter(response, fieldnames=['P.O', 'Customer', 'Request Date', 'Tail Number', 'Aircraft', 'Airport', 'FBO', 'Arrival Date', 'Departure Date', 'Complete By Date', 'Completion Date', 'Travel Fees', 'FBO Fees', 'Vendor Price Diff', 'Management Fees', 'Price', 'Services', 'Retainers'])
        writer.writeheader()

        searchText = self.request.data.get('searchText')
        status = self.request.data.get('status')
        airport = self.request.data.get('airport')
        customer = self.request.data.get('customer')
        fbo = self.request.data.get('fbo')
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

        qs = Job.objects.prefetch_related('job_service_assignments') \
                        .prefetch_related('job_retainer_service_assignments') \
                        .select_related('airport') \
                        .select_related('customer') \
                        .select_related('fbo') \
                        .select_related('aircraftType') \
                        .order_by('status') \
                        .all()    
        
        for additionalFee in additionalFees:
            if additionalFee == 'A':
                qs = qs.filter(travel_fees_amount_applied__gt=0)
            elif additionalFee == 'F':
                qs = qs.filter(fbo_fees_amount_applied__gt=0)
            elif additionalFee == 'M':
                qs = qs.filter(management_fees_amount_applied__gt=0)
            elif additionalFee == 'V':
                qs = qs.filter(vendor_higher_price_amount_applied__gt=0)

        if self.request.user.profile.customer:
            qs = qs.filter(customer=self.request.user.profile.customer)

        if searchText:
                qs = qs.filter(Q(tailNumber__icontains=searchText)
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

        if customer and customer != 'All':
            qs = qs.filter(customer_id=customer)
        

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
        
        show_job_price = True

        # check the customer settings if the user is a customer user to check if show_job_price is True
        if request.user.profile.customer:
            show_job_price_at_customer_level = request.user.profile.customer.customer_settings.show_job_price

            if show_job_price_at_customer_level:
                show_job_price_at_customer_user_level = request.user.profile.show_job_price

                if show_job_price_at_customer_user_level:
                    show_job_price = True
                
                else:
                    show_job_price = False

            else:
                show_job_price = False

        # add jobs to csv
        for job in qs:
            if job.estimatedETA:
                arrivalDate = job.estimatedETA.strftime('%m/%d/%Y %H:%M')
            else:
                arrivalDate = ''
            
            if job.estimatedETD:
                departureDate = job.estimatedETD.strftime('%m/%d/%Y %H:%M')
            else:
                departureDate = ''
            
            if job.completeBy:
                completeByDate = job.completeBy.strftime('%m/%d/%Y %H:%M')
            else:
                completeByDate = ''
            
            if job.completion_date:
                completionDate = job.completion_date.strftime('%m/%d/%Y %H:%M')
            else:
                completionDate = ''

            # add list of services to csv
            services = ''
            for service in job.job_service_assignments.all():
                services += service.service.name + ' | '

            # add list of retainers to csv
            retainers = ''
            for retainer in job.job_retainer_service_assignments.all():
                retainers += retainer.retainer_service.name + ' | '

            if show_job_price:
                writer.writerow({
                    'P.O': job.purchase_order,
                    'Customer': job.customer.name,
                    'Request Date': job.requestDate.strftime('%m/%d/%Y %H:%M'),
                    'Tail Number': job.tailNumber,
                    'Aircraft': job.aircraftType.name,
                    'Airport': job.airport.initials,
                    'FBO': job.fbo.name,
                    'Arrival Date': arrivalDate,
                    'Departure Date': departureDate,
                    'Complete By Date': completeByDate,
                    'Completion Date': completionDate,
                    'Travel Fees': job.travel_fees_amount_applied,
                    'FBO Fees': job.fbo_fees_amount_applied,
                    'Vendor Price Diff': job.vendor_higher_price_amount_applied,
                    'Management Fees': job.management_fees_amount_applied,
                    'Price': job.price,
                    'Services': services,
                    'Retainers': retainers
                })
            else:
                writer.writerow({
                    'P.O': job.purchase_order,
                    'Customer': job.customer.name,
                    'Request Date': job.requestDate.strftime('%m/%d/%Y %H:%M'),
                    'Tail Number': job.tailNumber,
                    'Aircraft': job.aircraftType.name,
                    'Airport': job.airport.initials,
                    'FBO': job.fbo.name,
                    'Arrival Date': arrivalDate,
                    'Departure Date': departureDate,
                    'Complete By Date': completeByDate,
                    'Completion Date': completionDate,
                    'Services': services,
                    'Retainers': retainers
                })

        
        return response


    def can_export(self, user):
        return user.is_superuser or user.is_staff or user.profile.customer or user.groups.filter(name='Account Managers').exists()