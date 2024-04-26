import json
from decimal import Decimal
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.response import Response

from api.models import (
        FBO,
        AirportAvailableFbo,
    )

class CreateFBOView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        fbo_name = request.data.get('name')
        is_public = request.data.get('public', True)
        airport_id = request.data.get('airport_id')

        # create fbo if it does not exist
        if FBO.objects.filter(name__iexact=fbo_name).exists():
            return Response({'error': 'FBO with name {} already exists'.format(fbo_name)}, status=status.HTTP_400_BAD_REQUEST)
        
        if not airport_id:
            return Response({'error': 'Airport ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        fbo = FBO.objects.create(
            name=fbo_name,
            public=is_public
        )

        AirportAvailableFbo.objects.create(
            airport_id=airport_id,
            fbo=fbo
        )
        
        return Response({'id': fbo.id, 'name': fbo.name}, status=status.HTTP_200_OK)