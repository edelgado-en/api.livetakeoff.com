from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from inventory.models import (
    LocationItem,
    LocationItemActivity
)

class LocationItemView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, id):
        location_item = LocationItem.objects.get(pk=id)

        action = request.data.get('action')
        quantity = request.data.get('quantity', None)

        if action == 'confirm':
            location_item.status = 'C'

        elif action == 'adjust':
            location_item.quantity = quantity
            location_item.status = 'U'

        elif action == 'move':
            location_item.status = 'M'
        
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        location_item.save()

        return Response({'success': 'Location item status updated'}, status=status.HTTP_200_OK)
    