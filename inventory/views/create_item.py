import json
from decimal import Decimal
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from inventory.models import (
        Item,
        LocationItem,
        ItemProvider,
        ItemTag
    )

class CreateItemView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        if not self.can_create_item(request.user):
            return Response({'error': 'You do not have permission to create an inventory'}, status=status.HTTP_403_FORBIDDEN)

        data = request.data

        name = data.get('name')
        description = data.get('description', None)
        areaId = data.get('areaId')
        measureUnitId = data.get('measureUnitId')
        costPerUnit = data.get('costPerUnit')
        tagIds = data.get('tagIds')
        providerIds = data.get('providerIds')
        locationItems = data.get('locationItems')
        photo = data.get('photo')

        costPerUnit = Decimal(costPerUnit.replace(',','.'))

        locationItems = json.loads(locationItems)

        item = Item.objects.create(
            name=name,
            description=description,
            area=areaId,
            measure_by=measureUnitId,
            cost_per_unit=costPerUnit,
            photo=photo,
            created_by=request.user
        )

        for locationItem in locationItems:
            brand_selected_id = None
            
            if locationItem['brandSelected'] != None:
                brand_selected_id = locationItem['brandSelected']['id']

            minimum_required = locationItem.get('minimumRequired', None)
            if minimum_required == '':
                minimum_required = None

            if minimum_required != None:
                minimum_required = int(locationItem['minimumRequired'])
            
            threshold = locationItem.get('alertAt', None)

            if threshold == '':
                threshold = None

            if threshold != None:
                threshold = int(locationItem['alertAt'])
            
            quantity = int(locationItem['quantity'])

            LocationItem.objects.create(
                item=item,
                location_id=locationItem['location']['id'],
                quantity=quantity,
                minimum_required=minimum_required,
                threshold=threshold,
                brand_id=brand_selected_id,
            )

        if tagIds != None:
            tagIds = json.loads(tagIds)
            for tagId in tagIds:
                ItemTag.objects.create(
                    item=item,
                    tag_id=tagId
                )

        if providerIds != None:
            providerIds = json.loads(providerIds)
            for providerId in providerIds:
                ItemProvider.objects.create(
                    item=item,
                    provider_id=providerId
                )

        return Response({'success': 'Item created successfully'}, status=status.HTTP_200_OK)
        

    def can_create_item(self, user):
        """
        Check if the user has permission to create an inventory item.
        """
        if user.is_superuser \
                 or user.is_staff \
                 or user.groups.filter(name='Account Managers').exists() \
                 or user.groups.filter(name='Internal Coordinators').exists():
            return True
        else:
            return False