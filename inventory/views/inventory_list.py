from django.db.models import Q, F
from rest_framework import (permissions,status)
from rest_framework .response import Response
from rest_framework.generics import ListAPIView
from inventory.serializers import (
        ItemSerializer,
    )

from api.pagination import CustomPageNumberPagination
from inventory.models import (
        Item
    )

class InventoryListView(ListAPIView):
    serializer_class = ItemSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        qs = Item.objects.all()
        return qs


    def post(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)