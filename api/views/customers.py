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
        name = self.request.data.get('name', '')
        open_jobs = self.request.data.get('open_jobs', False)
        closed_jobs = self.request.data.get('closed_jobs', False)
        has_flight_based_scheduled_cleaning = self.request.data.get('has_flight_based_scheduled_cleaning', False)

        user_profile = UserProfile.objects.get(user=self.request.user)
        is_customer = user_profile and user_profile.customer is not None

        qs = Customer.objects \
                       .filter(name__icontains=name, active=True) \
                       .order_by('name')

        # if open_jobs include only customers with open jobs. An open job is a job with status 'A' or 'U', or 'S' or 'W'
        if open_jobs:
            qs = qs.filter(jobs__status__in=['A', 'U', 'S', 'W']).distinct()
    
        if closed_jobs:
            qs = qs.filter(jobs__status__in=['C', 'I', 'T']).distinct()
        
        if has_flight_based_scheduled_cleaning:
            qs = qs.filter(customer_settings__enable_flight_based_scheduled_cleaning=True)

        if self.request.user.groups.filter(name='Internal Coordinators').exists():

            if not user_profile.enable_all_customers:
                user_customers = UserCustomer.objects.filter(user=self.request.user).all()

                if user_customers:
                    customer_ids = []
                    for user_customer in user_customers:
                        customer_ids.append(user_customer.customer.id)

                    qs = qs.filter(id__in=customer_ids)
        
        elif is_customer:
            user_customers = UserCustomer.objects.filter(user=self.request.user).all()
            if user_customers:
                customer_ids = []
                for user_customer in user_customers:
                    customer_ids.append(user_customer.customer.id)

                customer_ids.append(user_profile.customer.id)

                qs = qs.filter(id__in=customer_ids)
            else:
                # if no user_customers, return empty queryset
                qs = qs.none()

        return qs

    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)