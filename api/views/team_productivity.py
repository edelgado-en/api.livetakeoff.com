from django.db.models import Q, F
from django.db import models
from django.db.models import Count, Sum, Func
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from datetime import (date, datetime, timedelta)

from api.models import (
    ServiceActivity,
    RetainerServiceActivity,
    JobStatusActivity,
)

class TeamProductivityView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        if not self.can_view_dashboard(request.user):
            return Response({'error': 'You do not have permission to view this page'}, status=status.HTTP_403_FORBIDDEN)
        

        dateSelected = request.data.get('dateSelected')
        customer_id = request.data.get('customer_id', None)
        tailNumber = request.data.get('tailNumber', None)
        is_internal_report = request.data.get('is_internal_report', False)
        is_external_report = request.data.get('is_external_report', False)

        # get start date and end date based on the dateSelected value provided
        if dateSelected == 'yesterday':
            yesterday = datetime.now() - timedelta(days=1)
            start_date = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
            end_date = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59)
        
        elif dateSelected == 'last7Days':
            today = date.today()
            start_date = today - timedelta(days=7)
            end_date = datetime.now()

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


        # Get the total number of jobs with status I in the last 30 days by querying at the jobStatusActivity table
        qs = JobStatusActivity.objects.filter(
            Q(status__in=['I']) &
            Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        ).values('job__id').annotate(
            total=Count('job__id')
        ).values('total')

        if customer_id:
            qs = qs.filter(job__customer_id=customer_id)

        if tailNumber:
            qs = qs.filter(Q(job__tailNumber__icontains=tailNumber))
        
        if is_internal_report:
            qs = qs.filter(Q(job__vendor=None) | Q(job__vendor__is_external=False))

        if is_external_report:
            qs = qs.filter(~Q(job__vendor=None))
            qs = qs.filter(Q(job__vendor__is_external=True))

        total_jobs = 0
        for item in qs:
            total_jobs += item['total']
        
        grand_total_labor_time = 0
        # Sum the Job.labor_time from JobStatusActivity where the status = 'I'
        qs = JobStatusActivity.objects.filter(
            Q(status__in=['I']) &
            Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        )

        if customer_id:
            qs = qs.filter(job__customer_id=customer_id)

        if tailNumber:
            qs = qs.filter(Q(job__tailNumber__icontains=tailNumber))

        if is_internal_report:
            qs = qs.filter(Q(job__vendor=None) | Q(job__vendor__is_external=False))

        if is_external_report:
            qs = qs.filter(~Q(job__vendor=None))
            qs = qs.filter(Q(job__vendor__is_external=True))

        qs = qs.aggregate(Sum('job__labor_time'))['job__labor_time__sum']

        if qs:
            grand_total_labor_time = qs 
        
        # Get the total number of services with statuc C in the last 30 days by querying at the serviceActivity table
        qs = ServiceActivity.objects.filter(
            Q(status='C') &
            Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        ).values('service__name').annotate(
            total=Count('service__id')
        ).values('service__name', 'total')

        if customer_id:
            qs = qs.filter(job__customer_id=customer_id)

        if tailNumber:
            qs = qs.filter(Q(job__tailNumber__icontains=tailNumber))

        if is_internal_report:
            qs = qs.filter(Q(job__vendor=None) | Q(job__vendor__is_external=False))

        if is_external_report:
            qs = qs.filter(~Q(job__vendor=None))
            qs = qs.filter(Q(job__vendor__is_external=True))

        grand_total_services = 0
        for item in qs:
            grand_total_services += item['total']

        # Get the total number of retainer services with status C in the last 30 days by querying at the retainerServiceActivity table
        qs = RetainerServiceActivity.objects.filter(
            Q(status='C') &
            Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        ).values('retainer_service__name').annotate(
            total=Count('retainer_service__id')
        ).values('retainer_service__name', 'total')

        if customer_id:
            qs = qs.filter(job__customer_id=customer_id)

        if tailNumber:
            qs = qs.filter(Q(job__tailNumber__icontains=tailNumber))

        if is_internal_report:
            qs = qs.filter(Q(job__vendor=None) | Q(job__vendor__is_external=False))

        if is_external_report:
            qs = qs.filter(~Q(job__vendor=None))
            qs = qs.filter(Q(job__vendor__is_external=True))

        grand_total_retainer_services = 0
        for item in qs:
            grand_total_retainer_services += item['total']

        # Sum the total price from JobStatusActivity where the status = 'I' 
        total_jobs_revenue = JobStatusActivity.objects.filter(
             Q(status__in=['I']) &
             Q(activity_type='S') &
             Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        )

        if customer_id:
            total_jobs_revenue = total_jobs_revenue.filter(job__customer_id=customer_id)          

        if tailNumber:
            total_jobs_revenue = total_jobs_revenue.filter(Q(job__tailNumber__icontains=tailNumber))

        if is_internal_report:
            total_jobs_revenue = total_jobs_revenue.filter(Q(job__vendor=None) | Q(job__vendor__is_external=False))

        if is_external_report:
            total_jobs_revenue = total_jobs_revenue.filter(~Q(job__vendor=None))
            total_jobs_revenue = total_jobs_revenue.filter(Q(job__vendor__is_external=True))

        total_jobs_revenue = total_jobs_revenue.aggregate(Sum('job__price'))['job__price__sum']

        #####################################
        total_jobs_revenue_not_invoiced = JobStatusActivity.objects.filter(
             Q(status__in=['N']) &
             Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        )

        if customer_id:
            total_jobs_revenue_not_invoiced = total_jobs_revenue_not_invoiced.filter(job__customer_id=customer_id)          

        if tailNumber:
            total_jobs_revenue_not_invoiced = total_jobs_revenue_not_invoiced.filter(Q(job__tailNumber__icontains=tailNumber))

        if is_internal_report:
            total_jobs_revenue_not_invoiced = total_jobs_revenue_not_invoiced.filter(Q(job__vendor=None) | Q(job__vendor__is_external=False))

        if is_external_report:
            total_jobs_revenue_not_invoiced = total_jobs_revenue_not_invoiced.filter(~Q(job__vendor=None))
            total_jobs_revenue_not_invoiced = total_jobs_revenue_not_invoiced.filter(Q(job__vendor__is_external=True))

        total_jobs_revenue_not_invoiced = total_jobs_revenue_not_invoiced.aggregate(Sum('job__price'))['job__price__sum']

        # Sum total subcontractor_profit
        total_subcontractor_profit = JobStatusActivity.objects.filter(
             Q(status__in=['I']) &
             Q(activity_type='S') &
            ~Q(job__vendor=None) &
             Q(job__vendor__is_external=True) &
             Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        )

        if customer_id:
            total_subcontractor_profit = total_subcontractor_profit.filter(job__customer_id=customer_id)          

        if tailNumber:
            total_subcontractor_profit = total_subcontractor_profit.filter(Q(job__tailNumber__icontains=tailNumber))

        total_subcontractor_profit = total_subcontractor_profit.aggregate(Sum('job__subcontractor_profit'))['job__subcontractor_profit__sum']

        total_travel_fees_amount_applied = 0
        total_fbo_fees_amount_applied = 0
        total_vendor_higher_price_amount_applied = 0
        total_management_fees_amount_applied = 0

        # Sum total fees
        total_fees_applied = JobStatusActivity.objects.filter(
             Q(status__in=['I']) &
             Q(activity_type='S') &
             Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        )

        if customer_id:
            total_fees_applied = total_fees_applied.filter(job__customer_id=customer_id)          

        if tailNumber:
            total_fees_applied = total_fees_applied.filter(Q(job__tailNumber__icontains=tailNumber))

        if is_internal_report:
            total_fees_applied = total_fees_applied.filter(Q(job__vendor=None) | Q(job__vendor__is_external=False))

        if is_external_report:
            total_fees_applied = total_fees_applied.filter(~Q(job__vendor=None))
            total_fees_applied = total_fees_applied.filter(Q(job__vendor__is_external=True))

        total_travel_fees_amount_applied = total_fees_applied.aggregate(Sum('job__travel_fees_amount_applied'))['job__travel_fees_amount_applied__sum']

        total_fbo_fees_amount_applied = total_fees_applied.aggregate(Sum('job__fbo_fees_amount_applied'))['job__fbo_fees_amount_applied__sum']

        total_vendor_higher_price_amount_applied = total_fees_applied.aggregate(Sum('job__vendor_higher_price_amount_applied'))['job__vendor_higher_price_amount_applied__sum']

        total_management_fees_amount_applied = total_fees_applied.aggregate(Sum('job__management_fees_amount_applied'))['job__management_fees_amount_applied__sum']

        # Get the top 5 services in the last 30 days by querying the ServiceActivity table and join to Services Table to get the service name. The resulset should be service name with its corresponding times the service was completed in the last 30 days
        qs = ServiceActivity.objects.filter(
            Q(status='C') &
            Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        ).values('service__name').annotate(
            total=Count('service__id')
        ).values('service__name', 'total')

        if customer_id:
            qs = qs.filter(job__customer_id=customer_id)

        if tailNumber:
            qs = qs.filter(Q(job__tailNumber__icontains=tailNumber))

        qs = qs.order_by('-total')[:5]

        top_services = []
        # add a percentage value to each service which is calculated based on the top 5 services provided
        for item in qs:
            percentage = 0

            if grand_total_services > 0:
                percentage = round((item['total'] / grand_total_services) * 100, 2)
            top_services.append({
                'name': item['service__name'],
                'total': item['total'],
                'percentage': percentage
            })

        
        # Get the top 5 retainer services in the last 30 days by querying the RetainerServiceActivity table and join to RetainerServices Table to get the retainer service name. The resulset should be retainer service name with its corresponding times the retainer service was completed in the last 30 days
        qs = RetainerServiceActivity.objects.filter(
            Q(status='C') &
            Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        ).values('retainer_service__name').annotate(
            total=Count('retainer_service__id')
        ).values('retainer_service__name', 'total')

        if customer_id:
            qs = qs.filter(job__customer_id=customer_id)

        if tailNumber:
            qs = qs.filter(Q(job__tailNumber__icontains=tailNumber))

        qs = qs.order_by('-total')[:5]

        top_retainer_services = []
        # add a percentage value to each retainer service which is calculated based on the top 5 retainer services provided
        for item in qs:
            percentage = 0

            if grand_total_retainer_services > 0:
                percentage = round((item['total'] / grand_total_retainer_services) * 100, 2)

            top_retainer_services.append({
                'name': item['retainer_service__name'],
                'total': item['total'],
                'percentage': percentage
            })

        processed_vendors = []
        if not is_internal_report and not is_external_report:
            # Fetch Vendors that have at least one job invoiced in the last 30 days
            qs = JobStatusActivity.objects.filter(
                Q(status__in=['I']) &
                Q(activity_type='S') &
                Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
            ).values('job__vendor__id', 'job__vendor__name').annotate(
                total_jobs=Count('job__id'),
                total_price=Sum('job__price'),
                total_subcontractor_profit=Sum('job__subcontractor_profit'),
            ).values('job__vendor__id', 'job__vendor__name', 'total_jobs', 'total_price', 'total_subcontractor_profit')

            if customer_id:
                qs = qs.filter(job__customer_id=customer_id)

            if tailNumber:
                qs = qs.filter(Q(job__tailNumber__icontains=tailNumber))
            
            for item in qs:
                vendor_id = item['job__vendor__id']
                vendor_name = item['job__vendor__name']

                # Get the total number of services with statuc C for this vendor_id
                qs = ServiceActivity.objects.filter(
                    Q(status='C') &
                    Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date) &
                    Q(job__vendor_id=vendor_id)
                ).values('service__id').annotate(
                    total=Count('service__id')
                ).values('total')

                total_services = 0
                for service in qs:
                    total_services += service['total']

                # test
                t_subcontractor_profit = 0
                if item['total_subcontractor_profit']:
                    t_subcontractor_profit = item['total_subcontractor_profit']
                
                subcontractor_profit_percentage = 0

                if item['total_price'] > 0 and t_subcontractor_profit > 0:
                    subcontractor_profit_percentage = round((t_subcontractor_profit / item['total_price']) * 100, 2)

                processed_vendors.append({
                    'id': vendor_id,
                    'name': vendor_name,
                    'total_jobs': item['total_jobs'],
                    'revenue': item['total_price'],
                    'subcontractor_profit': t_subcontractor_profit,
                    'total_services': total_services,
                    'subcontractor_profit_percentage': subcontractor_profit_percentage
                })

            # sort by highest revenue first
            processed_vendors = sorted(processed_vendors, key=lambda k: k['revenue'], reverse=True)

        return Response({
            'total_jobs': total_jobs,
            'total_services': grand_total_services,
            'total_retainer_services': grand_total_retainer_services,
            'total_jobs_price': total_jobs_revenue,
            'total_jobs_price_not_invoiced': total_jobs_revenue_not_invoiced,
            'total_subcontractor_profit': total_subcontractor_profit,
            'total_travel_fees_amount_applied': total_travel_fees_amount_applied,
            'total_fbo_fees_amount_applied': total_fbo_fees_amount_applied,
            'total_vendor_higher_price_amount_applied': total_vendor_higher_price_amount_applied,
            'total_management_fees_amount_applied': total_management_fees_amount_applied,
            'total_labor_time': grand_total_labor_time,
            'top_services': top_services,
            'top_retainer_services': top_retainer_services,
            'vendors': processed_vendors
        }, status=status.HTTP_200_OK)


    def can_view_dashboard(self, user):
        if user.is_superuser or user.is_staff or user.groups.filter(name='Account Managers').exists():
            return True
        
        return False








        