from django.db.models import Q, F
from rest_framework import (permissions,status)
from rest_framework .response import Response
from rest_framework.generics import ListAPIView
from ..serializers import (
        JobScheduleSerializer,
    )

from ..pagination import CustomPageNumberPagination
from ..models import (
        JobSchedule
    )


class JobScheduleListView(ListAPIView):
    serializer_class = JobScheduleSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        qs = JobSchedule.objects.filter(is_deleted=False).order_by('-created_at')

        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)