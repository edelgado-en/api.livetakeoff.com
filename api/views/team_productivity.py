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
    Job,
    JobStatusActivity,
    UserProfile,
    PriceListEntries
)

class TeamProductivityView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        if not self.can_view_dashboard(request.user):
            return Response({'error': 'You do not have permission to view this page'}, status=status.HTTP_403_FORBIDDEN)
        

        dateSelected = request.data.get('dateSelected')
        customer_id = request.data.get('customer_id', None)
        tailNumber = request.data.get('tailNumber', None)

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

        grand_total_retainer_services = 0
        for item in qs:
            grand_total_retainer_services += item['total']

        
        # Sum the total price from JobStatusActivity where the status = 'I' 
        total_jobs_revenue = JobStatusActivity.objects.filter(
             Q(status__in=['I']) &
             Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        )

        if customer_id:
            total_jobs_revenue = total_jobs_revenue.filter(job__customer_id=customer_id)          

        if tailNumber:
            total_jobs_revenue = total_jobs_revenue.filter(Q(job__tailNumber__icontains=tailNumber))

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

        total_jobs_revenue_not_invoiced = total_jobs_revenue_not_invoiced.aggregate(Sum('job__price'))['job__price__sum']


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
            top_services.append({
                'name': item['service__name'],
                'total': item['total'],
                'percentage': round((item['total'] / grand_total_services) * 100, 2)
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
            top_retainer_services.append({
                'name': item['retainer_service__name'],
                'total': item['total'],
                'percentage': round((item['total'] / grand_total_retainer_services) * 100, 2)
            })


        # get the list of all users that completed services in the last 30 days. The resultSet should be the user first name, last name and avatar (by querying the userProfile table) with the total number of services and retainer services completed, and the total revenue generated by the user in the last 30 days. The revenue generated by each user is calculated based on service, aircraft type, and price list of the customer associated with the job for which the service was completed. The price is calculated only based on services, not retainer services.
        qs = ServiceActivity.objects.filter(
            Q(status='C') &
            Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        ).values('project_manager__id').annotate(
            total=Count('service__id')
        ).values('project_manager__id', 'total')

        if customer_id:
            qs = qs.filter(job__customer_id=customer_id)

        if tailNumber:
            qs = qs.filter(Q(job__tailNumber__icontains=tailNumber))

        processed_user_ids = []

        users = []
        for item in qs:
            user_id = item['project_manager__id']
            processed_user_ids.append(item['project_manager__id'])

            try:
                user_profile = UserProfile.objects.get(user=item['project_manager__id']) 
            except UserProfile.DoesNotExist:
                continue

            # get the total number of services this user has completed in the last 30 days by querying the ServiceActivity table
            qs = ServiceActivity.objects.filter(
                Q(status='C') &
                Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date) &
                Q(project_manager__id=item['project_manager__id'])
            ).values('service__id').annotate(
                total=Count('service__id')
            ).values('total')

            if customer_id:
                qs = qs.filter(job__customer_id=customer_id)

            if tailNumber:
                qs = qs.filter(Q(job__tailNumber__icontains=tailNumber))

            total_services = 0
            for service in qs:
                total_services += service['total']

            # get the total number of retainer services this user has completed in the last 30 days by querying the RetainerServiceActivity table
            qs_retainer = RetainerServiceActivity.objects.filter(
                Q(status='C') &
                Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date) &
                Q(project_manager_id=item['project_manager__id'])
            ).values('retainer_service__id').annotate(
                total=Count('retainer_service__id')
            ).values('total')

            if customer_id:
                qs_retainer = qs_retainer.filter(job__customer_id=customer_id)

            if tailNumber:
                qs_retainer = qs_retainer.filter(Q(job__tailNumber__icontains=tailNumber))


            # Sum the price of each service completed by this user in the last 30 days
            total_revenue = ServiceActivity.objects.filter(
                Q(status='C') &
                Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date) &
                Q(project_manager_id=item['project_manager__id'])
            )

            if customer_id:
                total_revenue = total_revenue.filter(job__customer_id=customer_id)

            if tailNumber:
                total_revenue = total_revenue.filter(Q(job__tailNumber__icontains=tailNumber))

            total_revenue = total_revenue.aggregate(Sum('price'))['price__sum']

            if total_revenue is None:
                total_revenue = 0
            
            total_retainer_services = 0
            for item in qs_retainer:
                total_retainer_services += item['total']

            avatar_url = user_profile.avatar.url if user_profile.avatar else None

            # Sum the Job.labor_time from JobStatusActivity where the status = 'C' for this project_manager_id
            s_total_labor_time = JobStatusActivity.objects.filter(
                Q(status='C') &
                Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date) &
                Q(user_id=user_id)
            )

            if customer_id:
                s_total_labor_time = s_total_labor_time.filter(job__customer_id=customer_id)

            if tailNumber:
                s_total_labor_time = s_total_labor_time.filter(Q(job__tailNumber__icontains=tailNumber))

            s_total_labor_time = s_total_labor_time.aggregate(Sum('job__labor_time'))['job__labor_time__sum']

            if s_total_labor_time is None:
                s_total_labor_time = 0

            users.append({
                'id': user_profile.user.id,
                'first_name': user_profile.user.first_name,
                'last_name': user_profile.user.last_name,
                'avatar': avatar_url,
                'total_services': total_services,
                'total_retainer_services': total_retainer_services,
                'total_revenue': total_revenue,
                'total_labor_time': s_total_labor_time
            })


        # get the list of all users that completed retainer services that have not been included in the list of users that completed services in the last 30 days. The resultSet should be the user first name, last name and avatar (by querying the userProfile table) with the total number of services and retainer services completed, and the total revenue generated by the user in the last 30 days. The revenue generated by each user is calculated based on service, aircraft type, and price list of the customer associated with the job for which the service was completed. The price is calculated only based on services, not retainer services.
        qs = RetainerServiceActivity.objects.filter(
            Q(status='C') &
            Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date)
        ).values('project_manager__id').annotate(
            total=Count('retainer_service__id')
        ).values('project_manager__id', 'total')

        if customer_id:
            qs = qs.filter(job__customer_id=customer_id)

        if tailNumber:
            qs = qs.filter(Q(job__tailNumber__icontains=tailNumber))

        for item in qs:
            user_id = item['project_manager__id']
            if item['project_manager__id'] not in processed_user_ids:
                processed_user_ids.append(item['project_manager__id'])

                try:
                    user_profile = UserProfile.objects.get(user=item['project_manager__id']) 
                except UserProfile.DoesNotExist:
                    continue

                # get the total number of services this user has completed in the last 30 days by querying the ServiceActivity table
                qs = ServiceActivity.objects.filter(
                    Q(status='C') &
                    Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date) &
                    Q(project_manager__id=item['project_manager__id'])
                ).values('service__id').annotate(
                    total=Count('service__id')
                ).values('total')

                if customer_id:
                    qs = qs.filter(job__customer_id=customer_id)

                if tailNumber:
                    qs = qs.filter(Q(job__tailNumber__icontains=tailNumber))

                total_services = 0
                for service in qs:
                    total_services += service['total']

                # get the total number of retainer services this user has completed in the last 30 days by querying the RetainerServiceActivity table
                qs_retainer = RetainerServiceActivity.objects.filter(
                    Q(status='C') &
                    Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date) &
                    Q(project_manager_id=item['project_manager__id'])
                ).values('retainer_service__id').annotate(
                    total=Count('retainer_service__id')
                ).values('total')

                if customer_id:
                    qs_retainer = qs_retainer.filter(job__customer_id=customer_id)

                if tailNumber:
                    qs_retainer = qs_retainer.filter(Q(job__tailNumber__icontains=tailNumber))

                # Sum the price of each service completed by this user in the last 30 days
                total_revenue = ServiceActivity.objects.filter(
                    Q(status='C') &
                    Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date) &
                    Q(project_manager_id=item['project_manager__id'])
                )

                if customer_id:
                    total_revenue = total_revenue.filter(job__customer_id=customer_id)

                if tailNumber:
                    total_revenue = total_revenue.filter(Q(job__tailNumber__icontains=tailNumber))

                total_revenue = total_revenue.aggregate(Sum('price'))['price__sum']

                total_retainer_services = 0
                for item in qs_retainer:
                    total_retainer_services += item['total']

                avatar_url = user_profile.avatar.url if user_profile.avatar else None

                if total_revenue is None:
                    total_revenue = 0

                # Sum the Job.labor_time from JobStatusActivity where the status = 'C' for this project_manager_id
                r_total_labor_time = JobStatusActivity.objects.filter(
                    Q(status='C') &
                    Q(timestamp__gte=start_date) & Q(timestamp__lte=end_date) &
                    Q(user_id=user_id)
                )

                if customer_id:
                    r_total_labor_time = r_total_labor_time.filter(job__customer_id=customer_id)

                if tailNumber:
                    r_total_labor_time = r_total_labor_time.filter(Q(job__tailNumber__icontains=tailNumber))

                r_total_labor_time = r_total_labor_time.aggregate(Sum('job__labor_time'))['job__labor_time__sum']

                if r_total_labor_time is None:
                    r_total_labor_time = 0

                users.append({
                    'id': user_profile.user.id,
                    'first_name': user_profile.user.first_name,
                    'last_name': user_profile.user.last_name,
                    'avatar': avatar_url,
                    'total_services': total_services,
                    'total_retainer_services': total_retainer_services,
                    'total_revenue': total_revenue,
                    'total_labor_time': r_total_labor_time
                })

        # sort users by highest total_revenue
        users = sorted(users, key=lambda k: k['total_revenue'], reverse=True)
           
        
        return Response({
            'total_jobs': total_jobs,
            'total_services': grand_total_services,
            'total_retainer_services': grand_total_retainer_services,
            'total_jobs_price': total_jobs_revenue,
            'total_jobs_price_not_invoiced': total_jobs_revenue_not_invoiced,
            'total_labor_time': grand_total_labor_time,
            'top_services': top_services,
            'top_retainer_services': top_retainer_services,
            'users': users
        }, status=status.HTTP_200_OK)


    def can_view_dashboard(self, user):
        if user.is_superuser or user.is_staff or user.groups.filter(name='Account Managers').exists():
            return True
        
        return False








        