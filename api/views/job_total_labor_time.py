from django.db.models import Q, Sum
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from datetime import datetime

from api.models import (
        Job
    )

class JobTotalLaborTimeDetail(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def post(self, request):
        searchText = self.request.data.get('searchText')
        job_status = self.request.data.get('status')
        airport = self.request.data.get('airport')
        customer = self.request.data.get('customer')

        requestedDateFrom = self.request.data.get('requestedDateFrom')
        requestedDateTo = self.request.data.get('requestedDateTo')

        completionDateFrom = self.request.data.get('completionDateFrom')
        completionDateTo = self.request.data.get('completionDateTo')

        qs = Job.objects.all()

        if searchText:
            qs = qs.filter(Q(tailNumber__icontains=searchText)
                            | Q(customer_purchase_order__icontains=searchText)
                            | Q(purchase_order__icontains=searchText)
                            )

        if job_status == 'All':
            # if customer user, do not include T status
            if self.request.user.profile.customer:
                qs = qs.filter(Q(status='C') | Q(status='I') | Q(status='A') | Q(status='S') | Q(status='U') | Q(status='W'))
            else:
                qs = qs.filter(Q(status='C') | Q(status='I') | Q(status='T'))

        else:
            qs = qs.filter(status=job_status)


        if airport and airport != 'All':
            qs = qs.filter(airport_id=airport)


        if customer and customer != 'All':
            qs = qs.filter(customer_id=customer)


        # apply date range filters
        if requestedDateFrom:
            qs = qs.filter(requestDate__gte=requestedDateFrom)

        if requestedDateTo:
            qs = qs.filter(requestDate__lte=requestedDateTo)

        if completionDateFrom:
            qs = qs.filter(completion_date__gte=completionDateFrom)
        
        if completionDateTo:
            qs = qs.filter(completion_date__lte=completionDateTo)

        qs = qs.aggregate(Sum('labor_time'))

        return Response({'total_labor_time': qs['labor_time__sum']}, status=status.HTTP_200_OK)


