from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User

from inventory.models import (
    LocationItem,
    LocationItemActivity,
    LocationItemBrand
)

from api.email_notification_service import EmailNotificationService

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
                                                cost=location_item.quantity * location_item.item.cost_per_unit,
                                                quantity=location_item.quantity,
                                                user=request.user)

        elif action == 'adjust':
            quantity = request.data.get('quantity', None)
            quantity = int(quantity)

            is_out_of_stock = False
            is_threshold_met = False

            delta_quantity = abs(quantity - location_item.quantity)
            delta_cost = delta_quantity * location_item.item.cost_per_unit

            activity_type = 'A'

            if quantity < location_item.quantity:
                activity_type = 'S'

                threshold = 0

                if location_item.threshold is not None:
                    threshold = location_item.threshold

                if quantity == 0:
                    is_out_of_stock = True

                elif threshold > 0 and quantity <= threshold:
                    is_threshold_met = True

            location_item.quantity = quantity

            # as per requirements, adjusting the quantity of an item will also confirm the item
            location_item.status = 'C'
            location_item.on_hold = False

            location_item.save()

            LocationItemActivity.objects.create(location_item=location_item,
                                                activity_type=activity_type,
                                                quantity=delta_quantity,
                                                cost=delta_cost,
                                                user=request.user)
            

            # also create an locationItemActivity for activity_type = "C" to confirm the item
            LocationItemActivity.objects.create(location_item=location_item,
                                                activity_type='C',
                                                quantity=quantity,
                                                cost=quantity * location_item.item.cost_per_unit,
                                                user=request.user)
            
            admins = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True) | Q(groups__name='Account Managers'))

            enable_notifications = location_item.location.enable_notifications

            if enable_notifications:
                if is_out_of_stock:
                    EmailNotificationService().send_inventory_out_of_stock_notification(location_item)
                
                elif is_threshold_met:
                    EmailNotificationService().send_inventory_threshold_met_notification(location_item)

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

            is_out_of_stock = False
            is_threshold_met = False

            threshold = 0
            total_moving_cost = 0

            if location_item.threshold is not None:
                threshold = location_item.threshold

            # update current location item quantity with the adjusted quantity
            if adjustedQuantity < 0:
                adjustedQuantity = 0

            if adjustedQuantity == 0:
                is_out_of_stock = True
            
            elif threshold > 0 and adjustedQuantity <= threshold:
                is_threshold_met = True

            location_item.quantity = adjustedQuantity
            location_item.status = 'U'
        
            location_item.save()

            admins = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True) | Q(groups__name='Account Managers'))

            enable_notifications = location_item.location.enable_notifications
            
            if enable_notifications:
                if is_out_of_stock:
                    EmailNotificationService().send_inventory_out_of_stock_notification(location_item)
                
                elif is_threshold_met:
                    EmailNotificationService().send_inventory_threshold_met_notification(location_item)

            total_moving_cost = movingQuantity * location_item.item.cost_per_unit

            LocationItemActivity.objects.create(location_item=location_item,
                                                activity_type='M',
                                                quantity=movingQuantity,
                                                cost=total_moving_cost,
                                                moved_from=location_item.location,
                                                moved_to=destination_location_item.location,
                                                user=request.user)

        elif action == 'update':
            minimum_required = request.data.get('minimumRequired', None)
            threshold = request.data.get('threshold', None)
            toggle_on_hold = request.data.get('toggleOnHold', None)

            if minimum_required is not None:
                if minimum_required == '':
                    minimum_required = 0

                location_item.minimum_required = minimum_required

            if threshold is not None:
                if threshold == '':
                    threshold = 0

                location_item.threshold = threshold

            if toggle_on_hold is not None:
                location_item.on_hold = not location_item.on_hold

            location_item.save()

        else:
            return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

        
        return Response({'success': 'Location item updated'}, status=status.HTTP_200_OK)
    

    def delete(self, request, id):
        location_item = LocationItem.objects.get(pk=id)

        # delete all the locationItemActivity entries for this location item
        LocationItemActivity.objects.filter(location_item=location_item).delete()

        # delete all the locationItemBrand entries for this location item
        LocationItemBrand.objects.filter(location_item=location_item).delete()

        # delete the location item
        location_item.delete()

        return Response({'success': 'Location item deleted'}, status=status.HTTP_200_OK)

        
    