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
        vendorid = self.kwargs.get(self.lookup_url_kwarg)
        vendor = Vendor.objects.get(pk=vendorid)

        return VendorFile.objects.filter(vendor=vendor).order_by('-id')
    
    def delete(self, request, *args, **kwargs):
        vendorid = self.kwargs.get(self.lookup_url_kwarg)
        vendor_file = VendorFile.objects.get(pk=vendorid)
        vendor_file.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)



        

