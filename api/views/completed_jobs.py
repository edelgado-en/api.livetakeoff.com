from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from ..pagination import CustomPageNumberPagination
from api.models import (Job, JobStatusActivity, PriceListEntries, ServiceActivity)
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
        customer = self.request.data.get('customer')

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

        qs = Job.objects.select_related('airport') \
                        .select_related('customer') \
                        .select_related('fbo') \
                        .select_related('aircraftType') \
                        .order_by('-completion_date') \
                        .all()

        # if customer use, then only show jobs for that customer
        if self.request.user.profile.customer:
            qs = qs.filter(customer=self.request.user.profile.customer)


        if searchText:
                qs = qs.filter(Q(tailNumber__icontains=searchText)
                               | Q(customer_purchase_order__icontains=searchText)
                               | Q(purchase_order__icontains=searchText)
                              )

        if status == 'All':
            # if customer user, do not include T status
            if self.request.user.profile.customer:
                qs = qs.filter(Q(status='C') | Q(status='I'))
            else:
                qs = qs.filter(Q(status='C') | Q(status='I') | Q(status='T'))


            # sort by status C first, then status I, and then status T
            qs = qs.order_by('status')

        else:
            qs = qs.filter(status=status)


        if airport and airport != 'All':
            qs = qs.filter(airport_id=airport)


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

        return qs



    def post(self, request, *args, **kwargs):
        if not self.can_see_completed_list(request.user):
            return Response({'error': 'You do not have permission to view completed jobs'}, status=status.HTTP_403_FORBIDDEN)


        return self.list(request, *args, **kwargs)


    def patch(self, request, *args, **kwargs):
        if not self.can_see_completed_list(request.user):
            return Response({'error': 'You do not have permission to edit completed jobs'}, status=status.HTTP_403_FORBIDDEN)

        job = get_object_or_404(Job, pk=kwargs['id'])

        serializer = JobAdminSerializer(job, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            JobStatusActivity.objects.create(job=job, user=request.user, status='I')

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

                    service_activity.price = service_price

                    service_activity.save(update_fields=['price'])

                except PriceListEntries.DoesNotExist:
                    continue

            return Response(serializer.data, status.HTTP_200_OK)
        
        return Response({'error': 'Missing Required Fields'}, status.HTTP_400_BAD_REQUEST)


    def can_see_completed_list(self, user):
        return not user.groups.filter(name='Project Managers').exists()