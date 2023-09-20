import json
from decimal import Decimal
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.response import Response

from api.models import (
        Airport,
        AirportAvailableFbo,
    )

class CreateAirportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        initials = request.data.get('initials')
        name = request.data.get('name')
        public = request.data.get('public', False)
        active = request.data.get('active', True)
        available_fbo_ids = request.data.get('available_fbo_ids', [])

        # create airport
        airport = Airport.objects.create(
            initials=initials,
            name=name,
            public=public,
            active=active
        )

        # create available fbos
        for fbo_id in available_fbo_ids:
            AirportAvailableFbo.objects.create(
                airport=airport,
                fbo_id=fbo_id
            )
        
        return Response({'id': airport.id}, status=status.HTTP_200_OK)