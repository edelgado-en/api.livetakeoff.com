import os
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from api.models import (VendorFile, Vendor)

from api.serializers import (VendorFileSerializer)

class VendorFileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = VendorFileSerializer
    lookup_url_kwarg = "vendorid"

    def post(self, request, *args, **kwargs):
        vendorId = self.kwargs.get(self.lookup_url_kwarg)
        vendor = get_object_or_404(Vendor, pk=vendorId)
        file = request.data.get('file')

        p = VendorFile(vendor=vendor,
                    uploaded_by=request.user,
                    file=file,
                    name=file.name,
                    size=file.size,
                    )
        
        p.save()

        serializer = VendorFileSerializer(p)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
