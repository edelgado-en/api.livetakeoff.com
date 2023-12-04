from rest_framework import (permissions, status)
from rest_framework .response import Response

from ..serializers import (CustomerSerializer)
from rest_framework.generics import ListAPIView
from ..pagination import CustomPageNumberPagination
from ..models import (Customer, UserProfile, UserCustomer)


class CustomersView(ListAPIView):
    queryset = Customer.objects.all().order_by('name')
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CustomerSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        name = self.request.data['name']
        open_jobs = self.request.data.get('open_jobs', False)
        closed_jobs = self.request.data.get('closed_jobs', False)

        user_profile = UserProfile.objects.get(user=self.request.user)
        is_customer = user_profile and user_profile.customer is not None

        if is_customer:
            # return empty queryset if user is customer
            return Customer.objects.none()
        


        qs = Customer.objects \
                       .filter(name__icontains=name, active=True) \
                       .order_by('name')

        # if open_jobs include only customers with open jobs. An open job is a job with status 'A' or 'U', or 'S' or 'W'
        if open_jobs:
            qs = qs.filter(jobs__status__in=['A', 'U', 'S', 'W']).distinct()
    
        if closed_jobs:
            qs = qs.filter(jobs__status__in=['C', 'I', 'T']).distinct()

        if self.request.user.groups.filter(name='Internal Coordinators').exists():
            user_customers = UserCustomer.objects.filter(user=self.request.user).all()

            if user_customers:
                customer_ids = []
                for user_customer in user_customers:
                    customer_ids.append(user_customer.customer.id)

                qs = qs.filter(id__in=customer_ids)


        return qs

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)