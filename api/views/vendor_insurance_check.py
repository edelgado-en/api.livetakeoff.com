from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User

from ..models import (
        Job,
        VendorFile,
    )

from datetime import (datetime, timedelta)

class VendorInsuranceCheckView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        user_id = self.request.data.get('user_id')
        job_id = self.request.data.get('job_id')

        is_vendor_insurance_uploaded = False
        is_vendor_w9_uploaded = False
        is_vendor_insurance_expired = False
        is_vendor_insurance_about_to_expire = False
        is_vendor_external = False

        vendor = None

        if job_id:
            job = get_object_or_404(Job, pk=job_id)

            if job.job_service_assignments.exists():
                vendor = job.job_service_assignments.first().vendor
            elif job.job_retainer_service_assignments.exists():
                vendor = job.job_retainer_service_assignments.first().vendor
        elif user_id:
            user = get_object_or_404(User, pk=user_id)
            vendor = user.profile.vendor

        if vendor:
            # check that this is an external vendor
            if vendor.is_external:
                is_vendor_external = True
                vendor_w9 = VendorFile.objects.filter(vendor=vendor, file_type='W').first()

                if vendor_w9:
                    is_vendor_w9_uploaded = True

                # check if the vendor has uploaded their insurance
                vendor_insurance = VendorFile.objects.filter(vendor=vendor, file_type='I').first()

                if vendor_insurance:
                    is_vendor_insurance_uploaded = True

                    now_naive = datetime.now().replace(tzinfo=None)

                    # check if the insurance has expired
                    if vendor_insurance.expiration_date:
                        expiration_date_naive = vendor_insurance.expiration_date.replace(tzinfo=None)
                        
                        if expiration_date_naive < now_naive:
                            is_vendor_insurance_expired = True
                        elif expiration_date_naive < now_naive + timedelta(days=30):
                            is_vendor_insurance_about_to_expire = True

        
        # return an object with is_vendor_insurance_uploaded, is_vendor_insurance_expired, is_vendor_insurance_about_to_expire
        return Response({
            'is_vendor_external': is_vendor_external,
            'is_vendor_insurance_uploaded': is_vendor_insurance_uploaded,
            'is_vendor_insurance_expired': is_vendor_insurance_expired,
            'is_vendor_insurance_about_to_expire': is_vendor_insurance_about_to_expire,
            'is_vendor_w9_uploaded': is_vendor_w9_uploaded,
        }, status=status.HTTP_200_OK)