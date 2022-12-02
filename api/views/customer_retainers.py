from django.db.models import F
from rest_framework import (permissions, status)
from rest_framework .response import Response

from ..serializers import (CustomerRetainerSerializer)
from rest_framework.generics import ListAPIView
from ..pagination import CustomPageNumberPagination
from ..models import (Customer, CustomerSettings)


class CustomerRetainersView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CustomerRetainerSerializer
    pagination_class = CustomPageNumberPagination


    def get_queryset(self):
        name = self.request.data['name']

        qs = Customer.objects \
                     .filter(customer_settings__retainer_amount__gt=0) \
                     .filter(name__icontains=name) \
                     .annotate(retainer_amount=F('customer_settings__retainer_amount')) \
                     .order_by('-retainer_amount')

        return qs


    def post(self, request, *args, **kwargs):
        if not self.can_view_retainers(request.user):
            return Response(status=status.HTTP_403_FORBIDDEN)

        return self.list(request, *args, **kwargs)


    def can_view_retainers(self, user):
        if user.is_superuser \
                or user.is_staff \
                or user.groups.filter(name='Account Managers').exists():
            return True
        
        return False
