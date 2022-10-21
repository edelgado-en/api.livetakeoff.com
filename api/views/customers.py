from rest_framework import (permissions, status)
from rest_framework .response import Response

from ..serializers import (CustomerSerializer)
from rest_framework.generics import ListAPIView
from ..pagination import CustomPageNumberPagination
from ..models import (Customer)


class CustomersView(ListAPIView):
    queryset = Customer.objects.all().order_by('name')
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CustomerSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        name = self.request.data['name']

        qs = Customer.objects \
                       .filter(name__icontains=name) \
                       .order_by('name')

        return qs

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)