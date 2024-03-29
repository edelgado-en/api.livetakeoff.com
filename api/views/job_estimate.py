from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from datetime import datetime

from django.contrib.auth.models import User

from ..serializers import (JobEstimateDetailSerializer)
from rest_framework.generics import ListAPIView
from api.models import JobEstimate

from ..pagination import CustomPageNumberPagination


class JobEstimateView(ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = JobEstimateDetailSerializer
    pagination_class = CustomPageNumberPagination


    def get_queryset(self):
        status = self.request.data.get('status')
        customer = self.request.data.get('customer')
        searchText = self.request.data.get('searchText')

        qs = JobEstimate.objects.select_related('customer') \
                             .select_related('aircraftType') \
                             .all()

        if searchText:
            qs = qs.filter(Q(tailNumber__icontains=searchText))

        if status != 'All':
            qs = qs.filter(status=status)


        # if the current user is a customer, only show estimates for that customer
        if self.request.user.profile.customer:
            qs = qs.filter(customer=self.request.user.profile.customer)
        else:
            if customer != 'All':
                qs = qs.filter(customer_id=customer)

        
        qs = qs.order_by(F('requested_at').desc(nulls_last=True))

        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    
    def delete(self, request, *args, **kwargs):
        estimate = get_object_or_404(JobEstimate, pk=kwargs['id'])

        estimate.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

