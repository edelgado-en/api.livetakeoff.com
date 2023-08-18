import json
from decimal import Decimal
from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.response import Response

from inventory.models import (
        Item,
        ItemProvider,
        ItemTag,
    )

class UpdateItemView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request):
        if not self.can_update_item(request.user):
            return Response({'error': 'You do not have permission to update an inventory item'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data

        item_id = data.get('itemId')
        name = data.get('name')
        description = data.get('description', None)
        areaId = data.get('areaId')
        measureUnitId = data.get('measureUnitId')
        costPerUnit = data.get('costPerUnit')
        tagIds = data.get('tagIds', [])
        providerIds = data.get('providerIds', [])

        # fetch Item for item_id
        item = Item.objects.get(id=item_id)

        #update Item
        item.name = name
        item.description = description
        item.area = areaId
        item.measure_by = measureUnitId
        item.cost_per_unit = costPerUnit
        item.save()

        # delete the existing tags and providers
        ItemTag.objects.filter(item=item).delete()
        ItemProvider.objects.filter(item=item).delete()

        for tagId in tagIds:
            ItemTag.objects.create(
                item=item,
                tag_id=tagId
            )

        for providerId in providerIds:
            ItemProvider.objects.create(
                item=item,
                provider_id=providerId
            )

        return Response({'success': 'Item updated successfully'}, status=status.HTTP_200_OK)
        

    def can_update_item(self, user):
        """
        Check if the user has permission to update an inventory item.
        """
        if user.is_superuser \
                 or user.is_staff \
                 or user.groups.filter(name='Account Managers').exists() \
                 or user.groups.filter(name='Internal Coordinators').exists():
            return True
        else:
            return False