from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from datetime import datetime

from inventory.serializers import (
    ItemDetailSerializer,
)

from inventory.models import (
        Item,
    )

class ItemDetailsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        item = get_object_or_404(Item, pk=id)

        serializer = ItemDetailSerializer(item)

        return Response(serializer.data, status=status.HTTP_200_OK)