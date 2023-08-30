from django.db.models import Q
from rest_framework import (permissions, status)

from inventory.serializers import (DailyGeneralStatsSerializer)
from rest_framework.generics import ListAPIView

from inventory.models import (DailyGeneralStats, DailyLocationStats)

from datetime import (date, datetime)

class DailyGeneralStatsListView(ListAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = DailyGeneralStatsSerializer

    def get_queryset(self):
        year = self.request.data.get('year', None)
        location_id = self.request.data.get('location_id', None)
        
        if location_id:
            qs = DailyLocationStats.objects \
                            .filter(location_id=location_id, date__year=year) \
                            .order_by('-date')
        else:
            qs = DailyGeneralStats.objects \
                          .filter(date__year=year) \
                            .order_by('-date')
            
        return qs
    
    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)