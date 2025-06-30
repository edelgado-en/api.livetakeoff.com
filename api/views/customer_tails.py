from django.db.models import Q, Case, When, Value, CharField
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.generics import ListAPIView
from ..pagination import CustomPageNumberPagination

from api.models import (CustomerTail)

from api.serializers.customer_tail import CustomerTailSerializer

class CustomerTailListView(ListAPIView):
    serializer_class = CustomerTailSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        searchText = self.request.data.get('searchText')
        status = self.request.data.get('status', 'All')
        customerId = self.request.data.get('customerId', 'All')

        qs = CustomerTail.objects.all()

        if searchText:
            qs = qs.filter(
                Q(tail_number__icontains=searchText)
            )

        if customerId != "All":
            qs = qs.filter(customer__id=customerId)

        if status != "All":
            qs = qs.filter(status=status)

        return qs

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)