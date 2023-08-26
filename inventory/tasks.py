from apscheduler.schedulers.background import BackgroundScheduler

from django.db.models import Q
from datetime import datetime
import json
from datetime import date

from api.email_util import EmailUtil

scheduler = BackgroundScheduler()

def collect_daily_inventory_stats():
    print('JOB STARTED: collect_daily_inventory_stats')

    title = 'INVETORY COLLECTOR JOB STARTED'

    body = f'''
    <div style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">INVENTORY COLLECTOR JOB STARTED</div>
    '''

    email_util = EmailUtil()
    email_util.send_email('enriquedelgado806@gmail.com', title, body)

    print('JOB COMPLETED: collect_daily_inventory_stats')


# run job every day at 11pm
scheduler.add_job(collect_daily_inventory_stats, 'cron', hour=23, minute=0, second=0)

# run job every 20 minutes
#scheduler.add_job(collect_daily_inventory_stats, 'interval', minutes=10)

scheduler.start()