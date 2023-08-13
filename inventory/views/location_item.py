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
            # this is the location id you use to find the corresponding location item entry to increase the quantity with movingQuantity
            destinationLocationId = request.data.get('destinationLocationId', None)

            # this is the new quantity to update in the current location item
            adjustedQuantity = request.data.get('adjustedQuantity', None)
            
            # this is the quantity that you add to the destionation location item
            movingQuantity = request.data.get('movingQuantity', None)

            # fetch location item for destination location and location_item.item
            destination_location_item = LocationItem.objects.get(location_id=destinationLocationId, item=location_item.item)

            # update destination location item quantity or create a new location item if it does not exits
            if destination_location_item:
                destination_location_item.quantity += movingQuantity
                destination_location_item.save()
            else:
                destination_location_item = LocationItem.objects.create(location_id=destinationLocationId,
                                                                        item=location_item.item,
                                                                        quantity=movingQuantity,
                                                                        status='U')

            # update current location item quantity with the adjusted quantity
            if adjustedQuantity < 0:
                adjustedQuantity = 0

            location_item.quantity = adjustedQuantity
            location_item.status = 'U'
        
        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        location_item.save()

        return Response({'success': 'Location item status updated'}, status=status.HTTP_200_OK)
    