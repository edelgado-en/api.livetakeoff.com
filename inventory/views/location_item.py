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

        if action == 'confirm':
            location_item.status = 'C'

            location_item.save()

            LocationItemActivity.objects.create(location_item=location_item,
                                                activity_type='C',
                                                quantity=location_item.quantity,
                                                user=request.user)

        elif action == 'adjust':
            quantity = request.data.get('quantity', None)
            quantity = int(quantity)

            activity_type = 'A'

            if quantity < location_item.quantity:
                activity_type = 'S'
            
            delta_quantity = abs(quantity - location_item.quantity)

            delta_cost = delta_quantity * location_item.item.cost_per_unit

            location_item.quantity = quantity
            location_item.status = 'U'

            location_item.save()

            LocationItemActivity.objects.create(location_item=location_item,
                                                activity_type=activity_type,
                                                quantity=delta_quantity,
                                                cost=delta_cost,
                                                user=request.user)

        elif action == 'move':
            # this is the location id you use to find the corresponding location item entry to increase the quantity with movingQuantity
            destinationLocationId = request.data.get('destinationLocationId', None)

            # this is the new quantity to update in the current location item
            adjustedQuantity = request.data.get('adjustedQuantity', None)
            
            # this is the quantity that you add to the destionation location item
            movingQuantity = request.data.get('movingQuantity', None)

            destination_location_item = None

            # fetch location item for destination location and location_item.item
            try:
                destination_location_item = LocationItem.objects.get(location_id=destinationLocationId, item=location_item.item)

                destination_location_item.quantity += movingQuantity
                destination_location_item.save()

            except LocationItem.DoesNotExist:
                destination_location_item = LocationItem.objects.create(location_id=destinationLocationId,
                                                                        item=location_item.item,
                                                                        quantity=movingQuantity,
                                                                        status='U')

            # update current location item quantity with the adjusted quantity
            if adjustedQuantity < 0:
                adjustedQuantity = 0

            location_item.quantity = adjustedQuantity
            location_item.status = 'U'
        
            location_item.save()

            LocationItemActivity.objects.create(location_item=location_item,
                                                activity_type='M',
                                                quantity=movingQuantity,
                                                moved_from=location_item.location,
                                                moved_to=destination_location_item.location,
                                                user=request.user)

        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        
        return Response({'success': 'Location item updated'}, status=status.HTTP_200_OK)
    