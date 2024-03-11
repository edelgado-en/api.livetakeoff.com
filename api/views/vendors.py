from django.db.models import Q
from rest_framework import (permissions, status)
from rest_framework.generics import ListAPIView

from api.serializers import (VendorSerializer)
from api.models import (Vendor, UserProfile)

class VendorsView(ListAPIView):
    queryset = Vendor.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = VendorSerializer

    def get_queryset(self):
        name = self.request.data.get('name', '')
        open_jobs = self.request.data.get('open_jobs', False)

        user_profile = UserProfile.objects.get(user=self.request.user)
        is_customer = user_profile and user_profile.customer is not None

        if is_customer:
            # return empty queryset if user is customer
            return Vendor.objects.none()

        qs = Vendor.objects \
                       .filter(name__icontains=name, active=True, is_external=True) \
                       .order_by('name')
        
        if open_jobs:
            qs = qs.filter(jobs__status__in=['A', 'U', 'S', 'W']).distinct()

        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)