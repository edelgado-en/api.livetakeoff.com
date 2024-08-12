from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User

from api.models import (Job)

class JobInvoiceDetailsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        if not self.can_view_invoice_details(request.user):
            return Response({'error': 'You do not have permission to view this job'}, status=status.HTTP_403_FORBIDDEN)

        job = get_object_or_404(Job, pk=id)

        invoice_details = {
            'job_id': job.id,
            'internal_additional_cost': job.internal_additional_cost if job.internal_additional_cost else 0
        }

        if job.vendor:
            invoice_details['vendor'] = {
                'id': job.vendor.id,
                'name': job.vendor.name,
                'charge': job.vendor_charge if job.vendor_charge else 0,
                'additional_cost': job.vendor_additional_cost if job.vendor_additional_cost else 0
            }

            if job.vendor_charge:
                invoice_details['subcontractor_profit'] = job.subcontractor_profit if job.subcontractor_profit else 0,

        return Response(invoice_details, status=status.HTTP_200_OK)


    def can_view_invoice_details(self, user):
        if user.is_superuser \
          or user.is_staff \
          or user.groups.filter(name='Account Managers').exists():
           return True

        return False