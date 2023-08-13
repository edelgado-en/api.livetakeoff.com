from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from inventory.models import (
    LocationItem
)

class LocationItemView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, id):
        location_item = LocationItem.objects.get(pk=id)

        item_status = request.data.get('status')

        location_item.status = item_status

        location_item.save()

        return Response({'success': 'Location item status updated'}, status=status.HTTP_200_OK)
    