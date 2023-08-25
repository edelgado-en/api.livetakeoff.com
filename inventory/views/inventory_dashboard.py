from django.db.models import Q, F
from django.db import models
from django.db.models import Count, Sum, Func
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from datetime import (date, datetime, timedelta)

from inventory.models import (
    LocationItemActivity,
    LocationItem
)

from api.models import UserProfile

class InventoryDashboardView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        if not self.can_view_dashboard(request.user):
            return Response({'error': 'You do not have permission to view this page'}, status=status.HTTP_403_FORBIDDEN)

        dateSelected = request.data.get('dateSelected')

        # get start date and end date based on the dateSelected value provided
        if dateSelected == 'current':
            # current means get all the data with no date restrictions
            start_date = None
            end_date = None
        
        elif dateSelected == 'last7Days':
            today = date.today()
            start_date = today - timedelta(days=7)
            end_date = today

        elif dateSelected == 'lastWeek':
            today = date.today()
            start_date = today - timedelta(days=today.weekday(), weeks=1)
            end_date = start_date + timedelta(days=6)

        elif dateSelected == 'MTD':
            today = date.today()
            start_date = date(today.year, today.month, 1)
            end_date = datetime.now()

        elif dateSelected == 'lastMonth':
            today = date.today()
            first = today.replace(day=1)
            lastMonth = first - timedelta(days=1)
            start_date = lastMonth.replace(day=1)
            
            # check if last month has 31 days or 30 days or 28 days
            if lastMonth.month == 1 or lastMonth.month == 3 \
                or lastMonth.month == 5 or lastMonth.month == 7 or lastMonth.month == 8 \
                or lastMonth.month == 10 or lastMonth.month == 12:
                end_date = lastMonth.replace(day=31)
            
            elif lastMonth.month == 4 or lastMonth.month == 6 or lastMonth.month == 9 or lastMonth.month == 11:
                end_date = lastMonth.replace(day=30)
            
            else:
                end_date = lastMonth.replace(day=28)

        elif dateSelected == 'lastQuarter':
            today = date.today()
            # get today's month and check it is in the first, second, third or fourth quarter. if it is first quarter, then get the previous year's last quarter
            if today.month in [1,2,3]:
                start_date = date(today.year - 1, 10, 1)
                end_date = date(today.year - 1, 12, 31)
            
            elif today.month in [4,5,6]:
                start_date = date(today.year, 1, 1)
                end_date = date(today.year, 3, 31)
            
            elif today.month in [7,8,9]:
                start_date = date(today.year, 4, 1)
                end_date = date(today.year, 6, 30)
            
            elif today.month in [10,11,12]:
                start_date = date(today.year, 7, 1)
                end_date = date(today.year, 9, 30)

        
        elif dateSelected == 'YTD':
            year = datetime.now().year
            start_date = datetime(year, 1, 1)
            end_date = datetime.now()
        
        elif dateSelected == 'lastYear':
            today = date.today()
            start_date = date(today.year - 1, 1, 1)
            end_date = date(today.year - 1, 12, 31)

        total_inventory_value = 0
        total_items_in_stock = 0
        total_expense = 0
        total_out_of_stock = 0
        total_low_stock = 0
        inventory_accuracy = 0
        popular_items = []
        items_with_highest_expense = []
        locations_with_expense = []
        user_with_stats = []

        date_range_specified = False
        if start_date and end_date:
            date_range_specified = True

        qs = LocationItemActivity.objects.filter(activity_type='A')
        if date_range_specified:
            qs = qs.filter(timestamp__range=(start_date, end_date))

        total_cost_value = qs.aggregate(Sum('cost'))['cost__sum']
        
        qs = LocationItemActivity.objects.filter(activity_type='S')
        if date_range_specified:
            qs = qs.filter(timestamp__range=(start_date, end_date))
        
        total_cost_subtracted = qs.aggregate(Sum('cost'))['cost__sum']
    
        total_expense = total_cost_subtracted

        total_inventory_value = total_cost_value - total_cost_subtracted

        qs = LocationItemActivity.objects.filter(activity_type='A')
        if date_range_specified:
            qs = qs.filter(timestamp__range=(start_date, end_date))

        total_items_added = qs.aggregate(Sum('quantity'))['quantity__sum']
        
        qs = LocationItemActivity.objects.filter(activity_type='S')
        if date_range_specified:
            qs = qs.filter(timestamp__range=(start_date, end_date))

        total_items_subtracted = qs.aggregate(Sum('quantity'))['quantity__sum']
        
        total_items_in_stock = total_items_added - total_items_subtracted

        # count locationItems where the quantity is zero
        total_out_of_stock = LocationItem.objects.filter(quantity=0).count()

        # count locationItems where the quantity is less or equal than minimum_required and bigger than zero
        total_low_stock = LocationItem.objects.filter(quantity__lte=F('minimum_required'),
                                                        quantity__gt=0, minimum_required__gt=1).count()

        # count all locationItems and count locationItems where status = 'C'. The percentage of accuracy is calculated by dividing the count of locationItems where status = 'C' by the total count of locationItems
        total_location_items = LocationItem.objects.all().count()
        total_confirmed_location_items = LocationItem.objects.filter(status='C').count()

        if total_location_items > 0:
            inventory_accuracy = (total_confirmed_location_items / total_location_items) * 100
            inventory_accuracy = round(inventory_accuracy, 2)


        qs = LocationItemActivity.objects.all()
        if date_range_specified:
            qs = qs.filter(timestamp__range=(start_date, end_date))

        total_location_item_activities = qs.count()

        # get the top 10 most popular items
        qs = LocationItemActivity.objects.all()
        if date_range_specified:
            qs = qs.filter(timestamp__range=(start_date, end_date))

        qs = qs.values('location_item__item__name')
        qs = qs.annotate(count=Count('location_item__item__name'))
        qs = qs.order_by('-count')[:10]
        
        for item in qs:
            popular_items.append({
                'name': item['location_item__item__name'],
                'count': item['count'],
                'percentage': round((item['count'] / total_location_item_activities) * 100, 2)
                })
            
        # get the top 10 items with the highest expense. Expense is determined by the summation of locationItemActivities where the activity_type is 'S'. The result set should include item name and the corresponding cost
        qs = LocationItemActivity.objects.filter(activity_type='S') 
        if date_range_specified:
            qs = qs.filter(timestamp__range=(start_date, end_date))

        qs = qs.values('location_item__item__name')
        qs = qs.annotate(cost=Sum('cost')) 
        qs = qs.order_by('-cost')[:10]
        
        for item in qs:
            items_with_highest_expense.append({
                'name': item['location_item__item__name'],
                'cost': item['cost'],
                'percentage': round((item['cost'] / total_expense) * 100, 2)
                })
            
        # get locations with the highest expense. Expense is determined by the summation of locationItemActivities where the activity_type is 'S'. The result set should include location name and the corresponding cost
        qs = LocationItemActivity.objects.filter(activity_type='S') 
        if date_range_specified:
            qs = qs.filter(timestamp__range=(start_date, end_date))

        qs = qs.values('location_item__location__name') 
        qs = qs.annotate(cost=Sum('cost')) 
        qs = qs.order_by('-cost')
        
        for item in qs:
            locations_with_expense.append({
                'name': item['location_item__location__name'],
                'cost': item['cost'],
                'percentage': round((item['cost'] / total_expense) * 100, 2)
                })
            
        # get the user id from locationItemActivity with the following information: total_transactions (this is the count of activities done by this user), total_additions (this is the count of activities of activity_type 'A' done by this user), total_subtractions (this is the count of activities of activity_type 'S' done by this user), total_moves (this is the count of activities of activity_type 'M' done by this user), inventory_expense (this is the sum of cost of activity_type 'S' done by this user)
        qs = LocationItemActivity.objects.values('user__id') 
        if date_range_specified:
            qs = qs.filter(timestamp__range=(start_date, end_date))

        qs = qs.annotate(total_transactions=Count('user__id'),
                            total_additions=Count('user__id', filter=Q(activity_type='A')),
                            total_subtractions=Count('user__id', filter=Q(activity_type='S')),
                            total_moves=Count('user__id', filter=Q(activity_type='M')),
                            inventory_expense=Sum('cost', filter=Q(activity_type='S'))) 
        qs = qs.order_by('-total_transactions')
        
        for item in qs:
            try:
                user_profile = UserProfile.objects.get(pk=item['user__id'])
            except UserProfile.DoesNotExist:
                continue
            
            avatar_url = user_profile.avatar.url if user_profile.avatar else None

            user_with_stats.append({
                'id': user_profile.user.id,
                'first_name': user_profile.user.first_name,
                'last_name': user_profile.user.last_name,
                'avatar': avatar_url,
                'total_transactions': item['total_transactions'],
                'total_additions': item['total_additions'],
                'total_subtractions': item['total_subtractions'],
                'total_moves': item['total_moves'],
                'inventory_expense': item['inventory_expense']
                })
            
        return Response({'total_inventory_value': total_inventory_value,
                         'total_items_in_stock': total_items_in_stock,
                         'total_expense': total_expense,
                         'total_out_of_stock': total_out_of_stock,
                         'total_low_stock': total_low_stock,
                         'inventory_accuracy': inventory_accuracy,
                         'popular_items': popular_items,
                         'items_with_highest_expense': items_with_highest_expense,
                         'locations_with_expense': locations_with_expense,
                         'user_with_stats': user_with_stats
                         }, status=status.HTTP_200_OK)

    
    def can_view_dashboard(self, user):
        if user.is_superuser or user.is_staff or user.groups.filter(name='Account Managers').exists():
            return True
        
        return False