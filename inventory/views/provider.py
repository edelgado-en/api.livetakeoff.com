from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from inventory.models import (
    Provider,
)

class ProviderView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        name = request.data.get('name')
        description = request.data.get('description', None)
        url = request.data.get('url', None)

        # check that the name does not exist ignore case
        provider = Provider.objects.filter(name__iexact=name).first()

        if provider:
            return Response({'error': 'A provider with that name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        provider = Provider.objects.create(name=name, description=description, url=url)

        return Response({'id': provider.id, 'name': provider.name}, status=status.HTTP_200_OK)