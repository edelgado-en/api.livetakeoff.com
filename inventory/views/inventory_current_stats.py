from django.db.models import Q, F
from django.db import models
from django.db.models import Count, Sum, Func
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from datetime import (date, datetime, timedelta)

from inventory.models import (
    LocationItemActivity,
    LocationItem,
    Item
)

from api.models import UserProfile

class InventoryCurrentStatsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        if not self.can_view_dashboard(request.user):
            return Response({'error': 'You do not have permission to view this page'}, status=status.HTTP_403_FORBIDDEN)

        # get locationItems get where the quantity is greater than zero and multiply item__cost_per_unit by locationItem__quantity in the same query
        total_value_in_stock = LocationItem.objects.filter(quantity__gt=0) \
                                                  .filter(location__active=True) \
                                .aggregate(total_value_out_of_stock=Sum(F('item__cost_per_unit') * F('quantity')))['total_value_out_of_stock']

        if total_value_in_stock is None:
            total_value_in_stock = 0

        # sum up the quantities of all locationItems
        total_quantity_in_stock = LocationItem.objects.filter(quantity__gt=0) \
                                             .filter(location__active=True) \
                                            .aggregate(total_quantity_in_stock=Sum('quantity'))['total_quantity_in_stock']
        
        if total_quantity_in_stock is None:
            total_quantity_in_stock = 0

        total_out_of_stock = LocationItem.objects.filter(quantity=0, on_hold=False, location__active=True).count()

        # minimum_required is not null, quantity is less than or equal to minimum_required, quantity is greater than zero
        total_low_stock = LocationItem.objects.filter(minimum_required__isnull=False, quantity__lte=F('minimum_required'), quantity__gt=0, minimum_required__gt=1, location__active=True).count()
        
        # sum up the quantities of all locationItems_quantity where the status = 'C'
        total_confirmed = LocationItem.objects.filter(status='C') \
                        .filter(location__active=True) \
                        .aggregate(total_confirmed=Sum('quantity'))['total_confirmed']

        # sum up the quantities of all locationItems_quantity where the status = 'U'
        total_unconfirmed = LocationItem.objects.filter(status='U') \
                            .filter(location__active=True) \
                        .aggregate(total_unconfirmed=Sum('quantity'))['total_unconfirmed']
        
        if total_confirmed is None:
            total_confirmed = 0

        if total_unconfirmed is None:
            total_unconfirmed = 0

        inventory_accuracy = 0

        if (total_confirmed + total_unconfirmed) > 0:
            inventory_accuracy = round(total_confirmed / (total_confirmed + total_unconfirmed) * 100, 2)


        # sum up the locationItem_quantities per locationItem_location__name. The resultset should include location name, total_quantity
        # also include the total cost per location. The total cost is calculated by locationItem_quantity * item_cost_per_unit
        qs = LocationItem.objects.filter(quantity__gt=0) \
                                .filter(location__active=True) \
                                .values('location__name') \
                                .annotate(total_quantity=Sum('quantity')) \
                                .annotate(total_cost=Sum(F('item__cost_per_unit') * F('quantity'))) \
                                .order_by('location__name')
        
        location_current_stats = []
        
        for q in qs:
            location_current_stats.append({
                'location': q['location__name'],
                'total_quantity': q['total_quantity'],
                'total_cost': q['total_cost'],
            })

            # add percentage to location_current_stats if total_quantity_in_stock is greater than zero
            if total_quantity_in_stock > 0:
                location_current_stats[-1]['percentage'] = round(q['total_quantity'] / total_quantity_in_stock * 100, 2)
            else:
                location_current_stats[-1]['percentage'] = 0

        # order location_current_stats by percentage. Highest percentage first
        location_current_stats = sorted(location_current_stats, key=lambda k: k['percentage'], reverse=True)

        # sum up the locationItem_quantities per locationItem__item_area. The resultset should include area name, total_quantity
        # also include the total cost per area. The total cost is calculated by locationItem_quantity * item_cost_per_unit
        qs = LocationItem.objects.filter(quantity__gt=0) \
                                .filter(location__active=True) \
                                .values('item__area') \
                                .annotate(total_quantity=Sum('quantity')) \
                                .annotate(total_cost=Sum(F('item__cost_per_unit') * F('quantity'))) \
                                .order_by('item__area')
        
        area_current_stats = []

        for q in qs:
            area_current_stats.append({
                'area': q['item__area'],
                'total_quantity': q['total_quantity'],
                'total_cost': q['total_cost'],
            })

            # add percentage to area_current_stats if total_quantity_in_stock is greater than zero
            if total_quantity_in_stock > 0:
                area_current_stats[-1]['percentage'] = round(q['total_quantity'] / total_quantity_in_stock * 100, 2)
            else:
                area_current_stats[-1]['percentage'] = 0

        # order area_current_stats by percentage. Highest percentage first
        area_current_stats = sorted(area_current_stats, key=lambda k: k['percentage'], reverse=True)
        
        # sum up the locationItem_quantities per locationItem__status per locationItem__location_name. The resultset should include location name, total_confirmed, total_unconfirmed
        # where total_confirmed is the sum of all locationItem_quantities where status = 'C' and total_unconfirmed is the sum of all locationItem_quantities where status = 'U'
        qs = LocationItem.objects.values('location__name') \
                                .filter(location__active=True) \
                                .annotate(total_confirmed=Sum('quantity', filter=Q(status='C'))) \
                                .annotate(total_unconfirmed=Sum('quantity', filter=Q(status='U'))) \
                                .order_by('location__name')
        
        location_accuracy_stats = []

        for q in qs:
            confirmed = q['total_confirmed'] if q['total_confirmed'] is not None else 0
            unconfirmed = q['total_unconfirmed'] if q['total_unconfirmed'] is not None else 0

            if (confirmed + unconfirmed) > 0:
                location_accuracy_stats.append({
                    'location': q['location__name'],
                    'total_confirmed': confirmed,
                    'total_unconfirmed': unconfirmed,
                })

                location_accuracy_stats[-1]['percentage'] = round(confirmed / (confirmed + unconfirmed) * 100, 2)
        
        # order location_accuracy_stats by percentage. Lowest percentage first
        location_accuracy_stats = sorted(location_accuracy_stats, key=lambda k: k['percentage'])

        # only get the top 5 location_accuracy_stats
        #location_accuracy_stats = location_accuracy_stats[:5]

        return Response({'total_value_in_stock': total_value_in_stock,
                         'total_quantity_in_stock': total_quantity_in_stock,
                         'total_out_of_stock': total_out_of_stock,
                         'total_low_stock': total_low_stock,
                         'inventory_accuracy': inventory_accuracy,
                         'total_confirmed': total_confirmed,
                         'total_unconfirmed': total_unconfirmed,
                         'location_current_stats': location_current_stats,
                         'area_current_stats': area_current_stats,
                         'location_accuracy_stats': location_accuracy_stats,
                         }, status=status.HTTP_200_OK)


    def can_view_dashboard(self, user):
        if user.is_superuser or user.is_staff \
                or user.groups.filter(name='Account Managers').exists() \
                or user.groups.filter(name='Internal Coordinators').exists():
            return True
        
        return False