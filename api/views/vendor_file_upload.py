import os
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from datetime import (date, datetime, timedelta)
import pytz
from email.utils import parsedate_tz, mktime_tz

from api.models import (VendorFile, Vendor)

from api.email_notification_service import EmailNotificationService

from api.serializers import (VendorFileSerializer)

class VendorFileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = VendorFileSerializer
    lookup_url_kwarg = "vendorid"

    def post(self, request, *args, **kwargs):
        shoul_notify_admins = False
        if self.request.user.profile.vendor and self.request.user.profile.vendor.is_external:
            vendor = self.request.user.profile.vendor
            should_notify_admins = True
        else:
            vendorId = self.kwargs.get(self.lookup_url_kwarg)
            vendor = get_object_or_404(Vendor, pk=vendorId)
        
        file = request.data.get('file')
        file_type = request.data.get('file_type', 'O')
        expiration_date = request.data.get('expiration_date', 'null')
        is_approved = request.data.get('is_approved', True)

        if expiration_date == 'null':
            expiration_date = None
        else :
            try:
                timestamp = mktime_tz(parsedate_tz(expiration_date))
                # Now it is in UTC
                expiration_date = datetime(1970, 1, 1) + timedelta(seconds=timestamp)
            
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            
        if is_approved == 'true':
            is_approved = True
        else:
            is_approved = False

        p = VendorFile(vendor=vendor,
                    uploaded_by=request.user,
                    file=file,
                    name=file.name,
                    size=file.size,
                    file_type=file_type,
                    expiration_date=expiration_date,
                    is_approved=is_approved
                    )
        
        p.save()

        if should_notify_admins:
            EmailNotificationService().notify_admins_vendor_file_upload(vendor, p)

        serializer = VendorFileSerializer(p)

        return Response(serializer.data, status=status.HTTP_201_CREATED)
