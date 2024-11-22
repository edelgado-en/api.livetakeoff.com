from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User

from api.models import (PriceList)

from api.serializers import (PriceListSerializer,)

class PricePlanDetailView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request, id):
        price_plan = get_object_or_404(PriceList, pk=id)
        serializer = PriceListSerializer(price_plan)

        return Response(serializer.data)