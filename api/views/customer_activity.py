from django.db.models import F
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from ..serializers import (
        CustomerActivitySerializer,
    )

from ..pagination import CustomPageNumberPagination

from ..models import JobStatusActivity

class CustomerActivityView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CustomerActivitySerializer
    pagination_class = CustomPageNumberPagination


    def get_queryset(self):
        # get all the job status activity for the customer associated with the current user
        # excluding ('P', 'Price Changed'),
        # and order by timestamp descending
        qs = JobStatusActivity.objects \
                                .filter(job__customer=self.request.user.profile.customer) \
                                .exclude(status__in=['P', 'Price Changed']) \
                                .order_by('-timestamp')

        # get the tailNumber from the job and attached to the queryset
        qs = qs.annotate(tailNumber=F('job__tailNumber'))

        return qs
