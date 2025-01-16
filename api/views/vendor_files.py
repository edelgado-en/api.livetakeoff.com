from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.contrib.auth.models import User

from api.models import (VendorFile, Vendor)

from api.serializers import VendorFileSerializer

class VendorFilesView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = VendorFileSerializer
    lookup_url_kwarg = "vendorid"

    def get_queryset(self):
        # if the current user is an external project manager, then return their corresponding vendor and ignore the vendorid
        if self.request.user.profile.vendor and self.request.user.profile.vendor.is_external:
            return VendorFile.objects.filter(vendor=self.request.user.profile.vendor).order_by('-id')

        if not self.request.user.is_staff \
            and not self.request.user.is_superuser \
            and not self.request.user.groups.filter(name='Account Managers').exists():
            return Response({'error': 'You do not have permission to delete vendor files'}, status=status.HTTP_403_FORBIDDEN)

        vendorid = self.kwargs.get(self.lookup_url_kwarg)
        vendor = Vendor.objects.get(pk=vendorid)

        return VendorFile.objects.filter(vendor=vendor).order_by('-id')
    
    def delete(self, request, *args, **kwargs):
        if not request.user.is_staff \
            and not request.user.is_superuser \
            and not request.user.groups.filter(name='Account Managers').exists():
            return Response({'error': 'You do not have permission to delete vendor files'}, status=status.HTTP_403_FORBIDDEN)

        vendorid = self.kwargs.get(self.lookup_url_kwarg)
        vendor_file = VendorFile.objects.get(pk=vendorid)
        vendor_file.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)



        

