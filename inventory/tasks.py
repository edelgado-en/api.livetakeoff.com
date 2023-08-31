from apscheduler.schedulers.background import BackgroundScheduler

from django.db.models import Q, F
from django.db import models
from django.db.models import Count, Sum, Func

from datetime import datetime
import json
from datetime import date

from inventory.models import (
    DailyGeneralStats,
    DailyLocationStats,
    Item,
    LocationItem,
    LocationItemActivity,
    Location,
    DailyStatsAudit
)

scheduler = BackgroundScheduler()

def collect_daily_inventory_stats():
    print('JOB STARTED: collect_daily_inventory_stats')

    today = datetime.now()


    # Check if there is a DailyStatsAudit object for today. If there is, then do not run the job. If there is not, then run the job and UPDATE (or create if there is no entry) the DailyStatsAudit object
    # This is to prevent the job from running multiple times in a day
    daily_stats_audit = DailyStatsAudit.objects.filter(last_updated=today.date()).first()

    if daily_stats_audit is not None:
        print('JOB ABORTED: collect_daily_inventory_stats')
        return

    # get locationItems get where the quantity is greater than zero and multiply item__cost_per_unit by locationItem__quantity in the same query
    total_value_in_stock = LocationItem.objects.filter(quantity__gt=0) \
                            .aggregate(total_value_out_of_stock=Sum(F('item__cost_per_unit') * F('quantity')))['total_value_out_of_stock']

    if total_value_in_stock is None:
        total_value_in_stock = 0

    # sum up the quantities of all locationItems
    total_quantity_in_stock = LocationItem.objects.filter(quantity__gt=0) \
                                        .aggregate(total_quantity_in_stock=Sum('quantity'))['total_quantity_in_stock']
    
    if total_quantity_in_stock is None:
        total_quantity_in_stock = 0

    total_items = Item.objects.count()

    start_date = datetime(today.year, today.month, today.day)
    end_date = datetime.now()

    # total_moving_transactions_today is calculated by the number of LocationItemActivity where the date is today and the activity_type is 'M'
    # LocationItemActivity uses timestamp instead of date, you need to collect all the timestamps from today and then filter by activity_type = 'M'
    total_moving_transactions_today = LocationItemActivity.objects \
                                        .filter(timestamp__range=(start_date, end_date), activity_type='M').count()
    
    if total_moving_transactions_today is None:
        total_moving_transactions_today = 0

    # total_moving_quantity_today is calculated by summing the quantity of all LocationItemActivity where the date is today and the activity_type is 'M'
    total_moving_quantity_today = LocationItemActivity.objects \
                                        .filter(timestamp__range=(start_date, end_date), activity_type='M') \
                                        .aggregate(total_moving_quantity_today=Sum('quantity'))['total_moving_quantity_today']

    if total_moving_quantity_today is None:
        total_moving_quantity_today = 0

    # total_moving_cost_today is calculated by summing the cost of all LocationItemActivity where the date is today and the activity_type is 'M'
    total_moving_cost_today = LocationItemActivity.objects \
                                        .filter(timestamp__range=(start_date, end_date), activity_type='M') \
                                        .aggregate(total_moving_cost_today=Sum('cost'))['total_moving_cost_today']

    if total_moving_cost_today is None:
        total_moving_cost_today = 0

    # total_additions_today is calculated by the sum of LocationItemActivity quantities where the date is today and the activity_type is 'A'
    total_additions_today = LocationItemActivity.objects \
                                        .filter(timestamp__range=(start_date, end_date), activity_type='A') \
                                        .aggregate(total_additions_today=Sum('quantity'))['total_additions_today']

    if total_additions_today is None:
        total_additions_today = 0

    # total_add_cost_today is calculated by the sum of LocationItemActivity cost where the date is today and the activity_type is 'A'
    total_add_cost_today = LocationItemActivity.objects \
                                        .filter(timestamp__range=(start_date, end_date), activity_type='A') \
                                        .aggregate(total_add_cost_today=Sum('cost'))['total_add_cost_today']
    
    if total_add_cost_today is None:
        total_add_cost_today = 0

    # total_subtractions_today is calculated by the sum of LocationItemActivity quantities where the date is today and the activity_type is 'S'
    total_subtractions_today = LocationItemActivity.objects \
                                        .filter(timestamp__range=(start_date, end_date), activity_type='S') \
                                        .aggregate(total_subtractions_today=Sum('quantity'))['total_subtractions_today']
    
    if total_subtractions_today is None:
        total_subtractions_today = 0

    # total_expense_today is calculated by the sum of LocationItemActivity cost where the date is today and the activity_type is 'S'
    total_expense_today = LocationItemActivity.objects \
                                        .filter(timestamp__range=(start_date, end_date), activity_type='S') \
                                        .aggregate(total_expense_today=Sum('cost'))['total_expense_today']
    
    if total_expense_today is None:
        total_expense_today = 0

    # Fetch DailyGeneralStats for today. Don't create a new entry if there is already one
    qs = DailyGeneralStats.objects.filter(date=today.date()).first()

    if qs is not None:
        # update existing entry
        qs.total_items = total_items
        qs.total_quantity = total_quantity_in_stock
        qs.total_cost = total_value_in_stock
        qs.total_moving_items = total_moving_transactions_today
        qs.total_moving_quantity = total_moving_quantity_today
        qs.total_moving_cost = total_moving_cost_today
        qs.total_additions = total_additions_today
        qs.total_add_cost = total_add_cost_today
        qs.total_subtractions = total_subtractions_today
        qs.total_expense = total_expense_today
        qs.save()

    else:
        DailyGeneralStats.objects.create(
            total_items=total_items,
            total_quantity=total_quantity_in_stock,
            total_cost=total_value_in_stock,
            total_moving_items=total_moving_transactions_today,
            total_moving_quantity=total_moving_quantity_today,
            total_moving_cost=total_moving_cost_today,
            total_additions=total_additions_today,
            total_add_cost=total_add_cost_today,
            total_subtractions=total_subtractions_today,
            total_expense=total_expense_today,
        )

    # get all locations and iterate through each location. Calculate all stats per location and create a DailyLocationStats object
    locations = Location.objects.all()

    for location in locations:
        # total_items is calculated by counting the number of unique items in LocationItem for this location
        total_items = LocationItem.objects.filter(location=location).values('item').distinct().count()

        # get locationItems get where the quantity is greater than zero and multiply item__cost_per_unit by locationItem__quantity in the same query
        total_value_in_stock = LocationItem.objects.filter(location=location, quantity__gt=0) \
                                .aggregate(total_value_out_of_stock=Sum(F('item__cost_per_unit') * F('quantity')))['total_value_out_of_stock']

        if total_value_in_stock is None:
            total_value_in_stock = 0

        # sum up the quantities of all locationItems
        total_quantity_in_stock = LocationItem.objects.filter(location=location, quantity__gt=0) \
                                                .aggregate(total_quantity_in_stock=Sum('quantity'))['total_quantity_in_stock']
        
        if total_quantity_in_stock is None:
            total_quantity_in_stock = 0

        # total_moving_transactions_today is calculated by the number of LocationItemActivity where the date is today and the activity_type is 'M'
        # LocationItemActivity uses timestamp instead of date, you need to collect all the timestamps from today and then filter by activity_type = 'M'
        total_moving_transactions_today = LocationItemActivity.objects \
                                            .filter(location_item__location=location, timestamp__range=(start_date, end_date), activity_type='M').count()
        
        if total_moving_transactions_today is None:
            total_moving_transactions_today = 0

        # total_moving_quantity_today is calculated by summing the quantity of all LocationItemActivity where the date is today and the activity_type is 'M'
        total_moving_quantity_today = LocationItemActivity.objects \
                                            .filter(location_item__location=location, timestamp__range=(start_date, end_date), activity_type='M') \
                                            .aggregate(total_moving_quantity_today=Sum('quantity'))['total_moving_quantity_today']

        if total_moving_quantity_today is None:
            total_moving_quantity_today = 0

        # total_moving_cost_today is calculated by summing the cost of all LocationItemActivity where the date is today and the activity_type is 'M'
        total_moving_cost_today = LocationItemActivity.objects \
                                            .filter(location_item__location=location, timestamp__range=(start_date, end_date), activity_type='M') \
                                            .aggregate(total_moving_cost_today=Sum('cost'))['total_moving_cost_today']

        if total_moving_cost_today is None:
            total_moving_cost_today = 0

        # total_additions_today is calculated by the sum of LocationItemActivity quantities where the date is today and the activity_type is 'A' for this location
        total_additions_today = LocationItemActivity.objects \
                                            .filter(location_item__location=location, timestamp__range=(start_date, end_date), activity_type='A') \
                                            .aggregate(total_additions_today=Sum('quantity'))['total_additions_today']
        
        if total_additions_today is None:
            total_additions_today = 0

        # total_add_cost_today is calculated by the sum of LocationItemActivity cost where the date is today and the activity_type is 'A' for this location
        total_add_cost_today = LocationItemActivity.objects \
                                            .filter(location_item__location=location, timestamp__range=(start_date, end_date), activity_type='A') \
                                            .aggregate(total_add_cost_today=Sum('cost'))['total_add_cost_today']
        
        if total_add_cost_today is None:
            total_add_cost_today = 0

        # total_subtractions_today is calculated by the sum of LocationItemActivity quantities where the date is today and the activity_type is 'S' for this location
        total_subtractions_today = LocationItemActivity.objects \
                                            .filter(location_item__location=location, timestamp__range=(start_date, end_date), activity_type='S') \
                                            .aggregate(total_subtractions_today=Sum('quantity'))['total_subtractions_today']
        
        if total_subtractions_today is None:
            total_subtractions_today = 0

        # total_expense_today is calculated by the sum of LocationItemActivity cost where the date is today and the activity_type is 'S' for this location
        total_expense_today = LocationItemActivity.objects \
                                            .filter(location_item__location=location, timestamp__range=(start_date, end_date), activity_type='S') \
                                            .aggregate(total_expense_today=Sum('cost'))['total_expense_today']
        
        if total_expense_today is None:
            total_expense_today = 0

        # Fetch DailyLocationStats for today and this location. Don't create a new entry if there is already one
        qs = DailyLocationStats.objects.filter(date=today.date(), location=location).first()

        if qs is not None:
            # update existing entry
            qs.total_items = total_items
            qs.total_quantity = total_quantity_in_stock
            qs.total_cost = total_value_in_stock
            qs.total_moving_items = total_moving_transactions_today
            qs.total_moving_quantity = total_moving_quantity_today
            qs.total_moving_cost = total_moving_cost_today
            qs.total_additions = total_additions_today
            qs.total_add_cost = total_add_cost_today
            qs.total_subtractions = total_subtractions_today
            qs.total_expense = total_expense_today
            qs.save()

        else:
            DailyLocationStats.objects.create(
                total_items=total_items,
                location=location,
                total_quantity=total_quantity_in_stock,
                total_cost=total_value_in_stock,
                total_moving_items=total_moving_transactions_today,
                total_moving_quantity=total_moving_quantity_today,
                total_moving_cost=total_moving_cost_today,
                total_additions=total_additions_today,
                total_add_cost=total_add_cost_today,
                total_subtractions=total_subtractions_today,
                total_expense=total_expense_today,
            )

    # update or create DailyStatsAudit with last_updated as today
    DailyStatsAudit.objects.update_or_create(
        last_updated=today.date(),
    )

    print('JOB COMPLETED: collect_daily_inventory_stats')

def deleteRepeatedDailyGeneralStats():
    print('JOB STARTED: deleteRepeatedDailyGeneralStats')

    # get all DailyGeneralStats
    daily_general_stats = DailyGeneralStats.objects.all()

    # iterate through each DailyGeneralStats
    for dgs in daily_general_stats:
        # get all DailyGeneralStats with the same date
        daily_general_stats_with_same_date = DailyGeneralStats.objects.filter(date=dgs.date)

        # if there are more than one DailyGeneralStats with the same date, then delete all of them except the first one
        if daily_general_stats_with_same_date.count() > 1:
            daily_general_stats_with_same_date.exclude(id=dgs.id).delete()

    # Do the same for DailyLocationStats
    daily_location_stats = DailyLocationStats.objects.all()

    for dls in daily_location_stats:
        daily_location_stats_with_same_date = DailyLocationStats.objects.filter(date=dls.date,
                                                                                location=dls.location)

        if daily_location_stats_with_same_date.count() > 1:
            daily_location_stats_with_same_date.exclude(id=dls.id).delete()

    print('JOB COMPLETED: deleteRepeatedDailyGeneralStats')

# run job every day at 8pm
scheduler.add_job(collect_daily_inventory_stats, 'cron', hour=20, minute=0, second=0)

# run job every 2 minutes
#scheduler.add_job(collect_daily_inventory_stats, 'interval', minutes=2)

# run job every 6 hours
scheduler.add_job(deleteRepeatedDailyGeneralStats, 'interval', hours=6)


scheduler.start()