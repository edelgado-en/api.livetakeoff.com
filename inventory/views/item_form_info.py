from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from inventory.models import (
    Brand,
    Provider,
    Tag,
    Location,
    Group,
    Item,
    LocationGroup
)

class ItemFormInfoView(APIView):
    """
    View to gather all the data needed to create a new inventory item.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        """
        Get all the data needed to create a new inventory item.
        """
        if not self.can_create_item(request.user):
            return Response({'error': 'You do not have permission to create a job'}, status=status.HTTP_403_FORBIDDEN)
        
        # fetch all brands
        brands = Brand.objects.all().order_by('name')

        brand_dtos = []

        for brand in brands:
            b = {
                'id': brand.id,
                'name': brand.name,
            }

            brand_dtos.append(b)

        # fetch all providers
        providers = Provider.objects.all().order_by('name')

        provider_dtos = []
        for provider in providers:
            p = {
                'id': provider.id,
                'name': provider.name,
            }

            provider_dtos.append(p)

        # fetch all tags
        tags = Tag.objects.all().order_by('name')

        tag_dtos = []
        for tag in tags:
            t = {
                'id': tag.id,
                'name': tag.name,
            }

            tag_dtos.append(t)
        
        # fetch all locations
        locations = Location.objects.all().order_by('name')

        location_dtos = []
        for location in locations:
            l = {
                'id': location.id,
                'name': location.name,
                'groups': []
            }

            # fetch all groups for this location
            location_groups = LocationGroup.objects.filter(location=location)

            for location_group in location_groups:
                g = {
                    'id': location_group.group.id,
                    'name': location_group.group.name,
                }

                l['groups'].append(g)

            location_dtos.append(l)
        
        # get all measure_by_choices from Item model
        measure_by_choices = Item.measure_by_choices
        
        measurement_dtos = []
        for measurement in measure_by_choices:
            m = {
                'id': measurement[0],
                'name': measurement[1],
            }

            measurement_dtos.append(m)


        # get all area_choices from Item model
        area_choices = Item.area_choices

        area_dtos = []
        for area in area_choices:
            a = {
                'id': area[0],
                'name': area[1],
            }

            area_dtos.append(a)

        # fetch all groups
        groups = Group.objects.all().order_by('name')

        group_dtos = []
        for group in groups:
            g = {
                'id': group.id,
                'name': group.name,
            }

            group_dtos.append(g)

        return Response({
            'brands': brand_dtos,
            'providers': provider_dtos,
            'tags': tag_dtos,
            'locations': location_dtos,
            'measurements': measurement_dtos,
            'areas': area_dtos,
            'groups': group_dtos,
        }, status.HTTP_200_OK)
        

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