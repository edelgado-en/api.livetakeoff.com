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

class InventoryHistoryStatsView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        if not self.can_view_dashboard(request.user):
            return Response({'error': 'You do not have permission to view this page'}, status=status.HTTP_403_FORBIDDEN)
        
        dateSelected = request.data.get('dateSelected')

        # get start date and end date based on the dateSelected value provided
        if dateSelected == 'today':
            # start_date should be the beginning of the day and end_date should be now
            today = datetime.now()
            start_date = datetime(today.year, today.month, today.day)
            end_date = datetime.now()

        elif dateSelected == 'yesterday':
            yesterday = datetime.now() - timedelta(days=1)
            start_date = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
            end_date = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
        
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

        # get the total expense for the time provided. The way to calculate total expense is by summing up the cost field in the locationItemActivity table for activity_type = 'S'
        total_inventory_expense = LocationItemActivity.objects \
                                       .filter(timestamp__range=(start_date, end_date), activity_type='S') \
                                       .aggregate(total_expense=Sum('cost'))['total_expense']
        

        # get the top 10 items with the highest expense. Expense is determined by the summation
        #  of locationItemActivities where the activity_type is 'S'.
        #  The result set should include item name and the corresponding cost
        qs = LocationItemActivity.objects \
                            .filter(timestamp__range=(start_date, end_date), activity_type='S') \
                            .values('location_item__item__name') \
                            .annotate(total_cost=Sum('cost')) \
                            .order_by('-total_cost')[:10]
        
        items_with_highest_expense = []
        for item in qs:
            items_with_highest_expense.append({
                'name': item['location_item__item__name'],
                'cost': item['total_cost'],
                })
            
            if total_inventory_expense > 0:
                items_with_highest_expense[-1]['percentage'] = round(item['total_cost'] / total_inventory_expense * 100, 2)
            else:
                items_with_highest_expense[-1]['percentage'] = 0
            
        # get the top 10 items with the highest number of transactions. A transaction is an entry in the locationItemActivity table
        #  The result set should include item name and the corresponding number of transactions
        qs = LocationItemActivity.objects \
                            .filter(timestamp__range=(start_date, end_date)) \
                            .values('location_item__item__name') \
                            .annotate(total_transactions=Count('id')) \
                            .order_by('-total_transactions')[:10]
        
        items_with_highest_transactions = []
        for item in qs:
            items_with_highest_transactions.append({
                'name': item['location_item__item__name'],
                'total_transactions': item['total_transactions'],
                })
            
        # Get all locations with their corresponsing expense. Expense is determined by the summation
        #  of locationItemActivities where the activity_type is 'S'.
        #  The result set should include location name and the corresponding expense
        qs = LocationItemActivity.objects \
                            .filter(timestamp__range=(start_date, end_date), activity_type='S') \
                            .values('location_item__location__name') \
                            .annotate(total_expense=Sum('cost')) \
                            .order_by('-total_expense')
        
        locations_with_expense = []
        for location in qs:
            locations_with_expense.append({
                'name': location['location_item__location__name'],
                'total_expense': location['total_expense'],
                })
            
            if total_inventory_expense > 0:
                locations_with_expense[-1]['percentage'] = round(location['total_expense'] / total_inventory_expense * 100, 2)
            else:
                locations_with_expense[-1]['percentage'] = 0
        
        # Get the user id from locationItemActivity with the following information:
        #  total_transactions (this is the count of activities done by this user),
        #  total_additions (this is the count of activities of activity_type 'A' done by this user),
        #  total_subtractions (this is the count of activities of activity_type 'S' done by this user),
        #  total_moves (this is the count of activities of activity_type 'M' done by this user),
        #  inventory_expense (this is the sum of cost of activity_type 'S' done by this user)
        # the result set should include the user_id, user_first_name, user_last_name, user__user_profile.avatar.url, total_transactions, total_additions, total_subtractions, total_moves, inventory_expense    
        qs = LocationItemActivity.objects \
                            .filter(timestamp__range=(start_date, end_date)) \
                            .values('user__id') \
                            .annotate(total_transactions=Count('id')) \
                            .annotate(total_additions=Count('id', filter=models.Q(activity_type='A'))) \
                            .annotate(total_subtractions=Count('id', filter=models.Q(activity_type='S'))) \
                            .annotate(total_moves=Count('id', filter=models.Q(activity_type='M'))) \
                            .annotate(inventory_expense=Sum('cost', filter=models.Q(activity_type='S'))) \
                            .order_by('-total_transactions')
        
        users_with_stats = []
        for item in qs:
            try:
                user_profile = UserProfile.objects.get(pk=item['user__id'])
            except UserProfile.DoesNotExist:
                continue
            avatar_url = user_profile.avatar.url if user_profile.avatar else None

            users_with_stats.append({
                'id': user_profile.user.id,
                'first_name': user_profile.user.first_name,
                'last_name': user_profile.user.last_name,
                'avatar': avatar_url,
                'total_transactions': item['total_transactions'],
                'total_additions': item['total_additions'],
                'total_subtractions': item['total_subtractions'],
                'total_moves': item['total_moves'],
                'inventory_expense': item['inventory_expense'] if item['inventory_expense'] is not None else 0,
                })
        
        return Response({
            'items_with_highest_expense': items_with_highest_expense,
            'items_with_highest_transactions': items_with_highest_transactions,
            'total_inventory_expense': total_inventory_expense,
            'locations_with_expense': locations_with_expense,
            'users_with_stats': users_with_stats
            })


    def can_view_dashboard(self, user):
        if user.is_superuser or user.is_staff or user.groups.filter(name='Account Managers').exists():
            return True
        
        return False