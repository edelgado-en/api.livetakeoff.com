from django.db.models import Q, F
from rest_framework import (permissions,status)
from rest_framework .response import Response
from rest_framework.generics import ListAPIView
from datetime import (date, datetime, timedelta)

from api.serializers import (
        ServiceActivitySerializer,
    )

from ..pagination import CustomPageNumberPagination
from api.models import (
        ServiceActivity,
        UserProfile,
        Job
    )

class TailServiceHistoryListView(ListAPIView):
    serializer_class = ServiceActivitySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        tail_number = self.request.data.get('tail_number', None)

        qs = ServiceActivity.objects \
                            .filter(job__tailNumber=tail_number, status='C') \
                            .order_by('-timestamp')[:10]

        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)