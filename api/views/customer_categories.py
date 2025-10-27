from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.generics import ListAPIView

from api.models import (CustomerCategory)

from api.serializers import (CustomerCategorySerializer)

from ..pagination import CustomPageNumberPagination

class CustomerCategoriesView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CustomerCategorySerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        name = self.request.data.get('name', '')
        customer_id = self.request.data.get('customer_id', None)

        qs = CustomerCategory.objects \
                          .filter(name__icontains=name)
        
        if customer_id:
            qs = qs.filter(customer_id=customer_id)

        return qs

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)