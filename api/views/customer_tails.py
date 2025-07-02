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
        service_due = self.request.data.get('service_due', 'All')

        qs = CustomerTail.objects.all()

        if searchText:
            qs = qs.filter(
                Q(tail_number__icontains=searchText)
            )

        if customerId != "All":
            qs = qs.filter(customer__id=customerId)

        if status != "All":
            qs = qs.filter(status=status)

        if service_due != "All":
            if service_due == "intLvl1Due":
                qs = qs.filter(is_interior_level_1_service_due=True)
            elif service_due == "intLvl2Due":
                qs = qs.filter(is_interior_level_2_service_due=True)
            elif service_due == "extLvl1Due":
                qs = qs.filter(is_exterior_level_1_service_due=True)
            elif service_due == "extLvl2Due":
                qs = qs.filter(is_exterior_level_2_service_due=True)

        return qs

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)