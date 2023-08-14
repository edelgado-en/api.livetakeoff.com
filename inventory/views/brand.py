from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from inventory.models import (
    Brand,
)

class BrandView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        name = request.data.get('name')
        description = request.data.get('description', None)

        # check that the name does not exist ignore case
        brand = Brand.objects.filter(name__iexact=name).first()

        if brand:
            return Response({'error': 'A brand with that name already exists'}, status=status.HTTP_400_BAD_REQUEST)

        brand = Brand.objects.create(name=name, description=description)

        return Response({'id': brand.id, 'name': brand.name}, status=status.HTTP_200_OK)