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

        open_jobs = self.request.data.get('open_jobs', False)

        qs = Customer.objects \
                       .filter(name__icontains=name, active=True) \
                       .order_by('name')

        # if open_jobs include only customers with open jobs. An open job is a job with status 'A' or 'U', or 'S' or 'W'
        if open_jobs:
            qs = qs.filter(jobs__status__in=['A', 'U', 'S', 'W']).distinct()
    
        return qs

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)