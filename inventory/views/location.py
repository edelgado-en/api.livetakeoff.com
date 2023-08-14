from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from inventory.models import (
    Location,
)

class LocationView(APIView):

    def post(self, request):
        name = request.data.get('name')
        description = request.data.get('description', None)

        # check that the name does not exist ignore case
        location = Location.objects.filter(name__iexact=name).first()

        if location:
            return Response({'error': 'A location with that name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        location = Location.objects.create(name=name, description=description)

        return Response({'id': location.id, 'name': location.name}, status=status.HTTP_200_OK)