from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.serializers import AirportSerializer
from api.models import Airport

class AirportDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        airport = get_object_or_404(Airport, pk=id)

        serializer = AirportSerializer(airport)
            
        return Response(serializer.data)