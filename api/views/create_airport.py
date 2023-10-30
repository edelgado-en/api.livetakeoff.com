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
        FBO
    )

class CreateAirportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        initials = request.data.get('initials')
        airport_name = request.data.get('name')
        public = request.data.get('public', False)
        active = request.data.get('active', True)
        available_fbos = request.data.get('available_fbos', [])

        # validate fbos first
        for fbo in available_fbos:
            fbo_name = fbo.get('name')

            # check fbo does not exists. If it does, return error
            if FBO.objects.filter(name__iexact=fbo_name).exists():
                return Response({'error': 'FBO with name {} already exists'.format(fbo_name)}, status=status.HTTP_400_BAD_REQUEST)


        airport = Airport.objects.create(
            initials=initials,
            name=airport_name,
            public=public,
            active=active
        )

        # create available fbos
        for fbo in available_fbos:
            fbo_name = fbo.get('name')
            public = fbo.get('public', False) 

            created_fbo = FBO.objects.create(
                name=fbo_name,
                public=public
            )

            AirportAvailableFbo.objects.create(
                airport=airport,
                fbo=created_fbo
            )
        
        return Response({'id': airport.id}, status=status.HTTP_200_OK)