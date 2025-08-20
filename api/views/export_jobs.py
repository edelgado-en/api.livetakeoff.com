from django.db.models import Q, F
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response

from django.contrib.auth.models import User

from ..serializers import (ExportJobSerializer)
from rest_framework.generics import ListAPIView
from api.models import ExportJob

from ..pagination import CustomPageNumberPagination

class ExportJobsView(ListAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = ExportJobSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        status = self.request.data.get('status', 'All')
        customer = self.request.data.get('customer', 'All')
        searchText = self.request.data.get('searchText')

        qs = ExportJob.objects.all()

        if searchText:
            qs = qs.filter(Q(filename__icontains=searchText))

        if status != 'All':
            qs = qs.filter(status=status)


        # if the current user is a customer, only show export jobs created by the current user
        if self.request.user.profile.customer:
            qs = qs.filter(user=self.request.user)
        else:
            if customer != 'All':
                qs = qs.filter(customer_id=customer)

        qs = qs.order_by('-created_at')

        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    
    def delete(self, request, *args, **kwargs):
        exportJob = get_object_or_404(ExportJob, pk=kwargs['id'])

        exportJob.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)