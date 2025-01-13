from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.generics import ListAPIView

from api.models import (CustomerFollowerEmail)

from api.serializers import (CustomerFollowerEmailSerializer)

from ..pagination import CustomPageNumberPagination

class CustomerFollowerEmailsView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CustomerFollowerEmailSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        email = self.request.data.get('email', '')
        customer_id = self.request.data.get('customer_id', None)

        qs = CustomerFollowerEmail.objects \
                          .filter(email__icontains=email)
        
        if customer_id:
            qs = qs.filter(customer_id=customer_id)


        return qs

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)