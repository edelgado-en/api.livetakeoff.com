from apscheduler.schedulers.background import BackgroundScheduler

from django.db.models import Q, F
from django.db import models
from django.db.models import Count, Sum, Func

from datetime import datetime, timedelta
import json
from datetime import date
import pytz

from zoneinfo import ZoneInfo

from django.contrib.auth.models import User

from api.flightaware_api_service import FlightawareApiService

from inventory.models import (
    DailyGeneralStats,
    DailyLocationStats,
    Item,
    LocationItem,
    LocationItemActivity,
    Location,
    DailyStatsAudit,
)

from api.models import (
    JobSchedule,
    Job,
    JobScheduleService,
    JobScheduleRetainerService,
    JobComments,
    JobServiceAssignment,
    JobRetainerServiceAssignment,
    JobTag,
    Tag,
    JobScheduleTag,
    JobStatusActivity,
    JobPhotos,
    VendorFile,
    Vendor,
    CustomerTail,
    TailAircraftLookup,
    TailIdent,
    Customer,
    ServiceActivity
)

from api.pricebreakdown_service import PriceBreakdownService
from api.email_notification_service import EmailNotificationService

import threading
import time

 # Use a lock to synchronize access to the task
task_lock = threading.Lock()

scheduler = BackgroundScheduler()

def collect_daily_inventory_stats():
    if not task_lock.acquire(blocking=False):
        print("Task is already running. Skipping.")
        return

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

    task_lock.release()

    print('JOB COMPLETED: collect_daily_inventory_stats')

def deleteRepeatedDailyGeneralStats():
    if not task_lock.acquire(blocking=False):
        print("Task is already running. Skipping.")
        return

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

    task_lock.release()

    print('JOB COMPLETED: deleteRepeatedDailyGeneralStats')

def createJobSchedules():
   
    if not task_lock.acquire(blocking=False):
        print("Task is already running. Skipping.")
        return
    
    try:
        print('JOB SCHEDULE STARTED: createJobSchedules')

        # Fetcha all JobSchedules where is_deleted is False
        job_schedules = JobSchedule.objects.filter(is_deleted=False)

        # iterate through job_schedules and create a job for each one
        for job_schedule in job_schedules:
            # get today's date ignoring the time
            today = date.today()

            # get job_schedule's start_date ignoring the time
            job_schedule_start_date = job_schedule.start_date.date()

            # check if job_Schedule_start_date is bigger or euqal to today
            if job_schedule_start_date <= today:
                if job_schedule.is_recurrent:
                    # get the repeat_every value
                    repeat_every = job_schedule.repeat_every

                    # get the last_job_created_at value
                    last_job_created_at = job_schedule.last_job_created_at

                    # check if it has been repeat_every days since the last job was created
                    if (last_job_created_at is None or ((today - last_job_created_at.date()).days >= repeat_every)):
                        handleCreateJob(job_schedule, today)

                else:
                    # Update job_schedule.is_deleted to True
                    job_schedule.is_deleted = True
                    job_schedule.save()

                    handleCreateJob(job_schedule, today)
        
        # Simulate a delay within the task (adjust as needed)
        time.sleep(20)

        print('JOB SCHEDULE COMPLETED: createJobSchedules')

    finally:
        task_lock.release()


def deleteRepeatedScheduledJobs():

    # Fetch jobs with job_schedule specified created today with the same customer, tailNumber, aircraftType, airport, fbo, comment and job.schedule within 20 seconds of each other and update the second one with status = 'T'
    # This is to prevent the job from being created twice
    jobs = Job.objects.filter(job_schedule__isnull=False, status='U').order_by('created_at')

    for i in range(len(jobs) - 1):
        if jobs[i].customer == jobs[i+1].customer and \
            jobs[i].tailNumber == jobs[i+1].tailNumber and \
            jobs[i].aircraftType == jobs[i+1].aircraftType and \
            jobs[i].airport == jobs[i+1].airport and \
            jobs[i].fbo == jobs[i+1].fbo and \
            (jobs[i].job_schedule == jobs[i+1].job_schedule) and \
            (jobs[i+1].created_at - jobs[i].created_at).seconds <= 20:
            jobs[i+1].status = 'T'
            jobs[i+1].save()
    

def deletePhotosOlderThanOneYear():
    #Fetch all the JobPhotos where the created_at date is older than one year from today
    job_photos = JobPhotos.objects.filter(created_at__lt=datetime.now() - timedelta(days=365))

    #Iterate through job_photos and delete each one
    for job_photo in job_photos:
        # this deletes from Cloudinary!
        job_photo.image.delete()
        # now delete the instance from the database
        job_photo.delete()


def handleCreateJob(job_schedule, today):
    newYorkTz = pytz.timezone("UTC") 

    # get today in newYorkTz
    n_today = datetime.now(newYorkTz).date()
    today_label = n_today.strftime("%Y%m%d")


    # Generate purchase order: current day + number of job received that day.
    #  So if today is 2019-01-01 and we have received 3 jobs today already, the purchase order will be 20190101-4
    jobs_created_today = Job.objects.filter(created_at__contains=n_today).count()

    purchase_order = today_label + '-' + str(jobs_created_today + 1)

    # create a job
    job = Job.objects.create(
        status='U',
        purchase_order=purchase_order,
        customer=job_schedule.customer,
        tailNumber=job_schedule.tailNumber,
        aircraftType=job_schedule.aircraftType,
        airport=job_schedule.airport,
        fbo=job_schedule.fbo,
        created_by=job_schedule.created_by,
        job_schedule=job_schedule,
    )

    # check if job_schedule.comment is not None and it is not empty
    if job_schedule.comment is not None and job_schedule.comment != '':
        # create job comments
        JobComments.objects.create(
            job=job,
            comment=job_schedule.comment,
            author=job_schedule.created_by,
        )

    # create job service assignments
    job_schedule_services = JobScheduleService.objects.filter(job_schedule=job_schedule)

    for job_schedule_service in job_schedule_services:
        JobServiceAssignment.objects.create(
            job=job,
            service=job_schedule_service.service,
        )

    # create job retainer service assignments
    job_schedule_retainer_services = JobScheduleRetainerService.objects.filter(job_schedule=job_schedule)

    for job_schedule_retainer_service in job_schedule_retainer_services:
        JobRetainerServiceAssignment.objects.create(
            job=job,
            retainer_service=job_schedule_retainer_service.retainer_service,
        )

    price_breakdown = PriceBreakdownService().get_price_breakdown(job)
    job.price = price_breakdown.get('totalPrice')
    job.travel_fees_amount_applied = price_breakdown.get('total_travel_fees_amount_applied')
    job.fbo_fees_amount_applied = price_breakdown.get('total_fbo_fees_amount_applied')
    job.vendor_higher_price_amount_applied = price_breakdown.get('total_vendor_higher_price_amount_applied')
    job.management_fees_amount_applied = price_breakdown.get('total_management_fees_amount_applied')

    job.save()
    
    JobStatusActivity.objects.create(job=job, user=job_schedule.created_by, status='U')

    job_schedule_tags = JobScheduleTag.objects.filter(job_schedule=job_schedule)

    for job_schedule_tag in job_schedule_tags:
        JobTag.objects.create(
            job=job,
            tag=job_schedule_tag.tag,
        )

    #Fetch a Tag with name 'Scheduled', if it does not exist, create it
    scheduled_tag = Tag.objects.filter(name='Scheduled').first()

    if scheduled_tag is None:
        scheduled_tag = Tag.objects.create(name='Scheduled', short_name='Scheduled')

    # create job tag
    JobTag.objects.create(
        job=job,
        tag=scheduled_tag,
    )

    # update job_schedule.last_job_created_at
    job_schedule.last_job_created_at = today
    job_schedule.save()

    EmailNotificationService().send_scheduled_job_created_notification(job_schedule)



def check_vendor_insurance_expiration():
    vendors = Vendor.objects.filter(is_external=True, active=True)

    vendors_to_report = []

    # Iterate through vendors and check if they have a VendorFile with file_type == 'I'
    for vendor in vendors:
        vendor_to_report = {
            'name': vendor.name,
            'has_no_insurance': False,
            'insurance_about_to_expire': False,
            'insurance_expired': False,
            'ok': True
        }

        # vendor.emails can be a string of comma separated emails. It can be only one email or multiple emails or empty
        emails = []

        if vendor.emails is not None and vendor.emails != '':
            emails = vendor.emails.split(',')
        
        vendor_to_report['emails'] = emails

        vendor_file = VendorFile.objects.filter(vendor=vendor, file_type='I').first()

        if vendor_file is not None:
            expiration_date = vendor_file.expiration_date

            today = date.today()

            # convert today to datetime
            today = datetime(today.year, today.month, today.day)
            
            # make naive
            today = today.replace(tzinfo=None)
            expiration_date = expiration_date.replace(tzinfo=None)

            # check if the insurance has expired
            if expiration_date < today:
                vendor_to_report['insurance_expired'] = True
                vendor_to_report['ok'] = False

            # check if the expiration date is within 30 days
            elif (expiration_date - today).days <= 30:
                vendor_to_report['insurance_about_to_expire'] = True
                vendor_to_report['ok'] = False

        else:
            vendor_to_report['has_no_insurance'] = True
            vendor_to_report['ok'] = False

        # add vendor_to_report to vendors_to_report
        vendors_to_report.append(vendor_to_report)

        # if vendor_to_report['ok'] is False, and vendor_to_report['emails'] is not empty, send an email to the emails
        if vendor_to_report['ok'] is False and len(vendor_to_report['emails']) > 0:
            EmailNotificationService().send_vendor_insurance_notification(vendor_to_report)

    
    EmailNotificationService().send_admin_vendor_insurance_notification(vendors_to_report)
                

def start_scheduler():
    # run job every day at 8pm
    scheduler.add_job(collect_daily_inventory_stats, 'cron', hour=20, minute=0, second=0)

    # run job every 6 hours
    scheduler.add_job(deleteRepeatedDailyGeneralStats, 'interval', hours=6)

    # run job every day at 4am
    scheduler.add_job(createJobSchedules, 'cron', hour=4, minute=0, second=0)

    #run job every day at 4:10 am
    scheduler.add_job(deleteRepeatedScheduledJobs, 'cron', hour=4, minute=10, second=0)

    #run job once a month on the first day of the month at 4:00 am
    scheduler.add_job(deletePhotosOlderThanOneYear, 'cron', day=1, hour=4, minute=0, second=0)

    # run check_vendor_insurance_expiration every 15 days at 5pm
    scheduler.add_job(check_vendor_insurance_expiration, 'cron', day='1,15', hour=17, minute=0, second=0)

    scheduler.start()