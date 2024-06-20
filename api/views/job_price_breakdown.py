from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from api.pricebreakdown_service import PriceBreakdownService

from api.models import (Job, CustomerSettings)

class JobPriceBreakdownView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, id):
        job = Job.objects.prefetch_related('job_service_assignments') \
                         .select_related('customer__customer_settings__price_list') \
                         .get(pk=id)

        if not self.can_see_price_breakdown(request.user, job):
            return Response({'error': 'You do not have permission to see the price breakdown'}, status=status.HTTP_403_FORBIDDEN)


        price_breakdown = PriceBreakdownService().get_price_breakdown(job)

        price_breakdown['totalPrice'] = f"{price_breakdown['totalPrice']:,.2f}"

        return Response(price_breakdown, status=status.HTTP_200_OK)


    def can_see_price_breakdown(self, user, job):
        # if user is customer and it matches the job customer, user should have permission to see price breakdown
        # and the customer setting Show Job Price is enabled
        if user.profile.customer \
                 and user.profile.customer == job.customer \
                 and job.customer.customer_settings.show_job_price:
            return True


        if user.is_superuser \
            or user.is_staff \
            or user.profile.show_job_price \
            or user.groups.filter(name='Account Managers').exists():
            return True

        return False