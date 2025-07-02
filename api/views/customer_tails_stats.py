from django.db.models import Q
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.models import CustomerTail

class CustomerTailStatsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        searchText = request.data.get('searchText')
        tail_status = request.data.get('status', 'All')
        customerId = request.data.get('customerId', 'All')
        service_due = self.request.data.get('service_due', 'All')

        qs = CustomerTail.objects.all()

        if searchText:
            qs = qs.filter(
                Q(tail_number__icontains=searchText)
            )
        if customerId != "All":
            qs = qs.filter(customer__id=customerId)
        
        if tail_status != "All":
            qs = qs.filter(status=tail_status)

        if service_due != "All":
            if service_due == "intLvl1Due":
                qs = qs.filter(is_interior_level_1_service_due=True)
            elif service_due == "intLvl2Due":
                qs = qs.filter(is_interior_level_2_service_due=True)
            elif service_due == "extLvl1Due":
                qs = qs.filter(is_exterior_level_1_service_due=True)
            elif service_due == "extLvl2Due":
                qs = qs.filter(is_exterior_level_2_service_due=True)

        total_tails = qs.count()
        status_s_count = qs.filter(status='S').count()
        status_o_count = qs.filter(status='O').count()
        status_n_count = qs.filter(status='N').count()
        
        data = {
            'total_tails': total_tails,
            'total_tails_w_service_due': status_s_count,
            'total_tails_ok': status_o_count,
            'total_tails_w_no_flight_history': status_n_count
        }
        return Response(data, status=status.HTTP_200_OK)
