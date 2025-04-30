from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from datetime import (date, datetime, timedelta)
import pytz
from email.utils import parsedate_tz, mktime_tz

from api.pricebreakdown_service import PriceBreakdownService
from api.email_notification_service import EmailNotificationService
from api.sms_notification_service import SMSNotificationService

import threading

from ..models import (
        Job,
        Service,
        RetainerService,
        AircraftType,
        Airport,
        Customer,
        FBO,
        JobComments,
        JobPhotos,
        JobServiceAssignment,
        JobRetainerServiceAssignment,
        JobStatusActivity,
        TailAircraftLookup,
        TailServiceLookup,
        TailRetainerServiceLookup,
        UserProfile,
        JobEstimate,
        Tag,
        JobTag,
        UserEmail,
        LastProjectManagersNotified,
        JobAcceptanceNotification,
        CustomerFollowerEmail,
        JobFollowerEmail,
        TailIdent
    )

class CreateJobView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):

        if not self.can_create_job(request.user):
            return Response({'error': 'You do not have permission to create a job'}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data

        tailNumber = data['tail_number']

        # remove trail spaces from tailNumber from the front and back
        tailNumber = tailNumber.strip()

        # if user is customer, get customer from user profile
        user_profile = UserProfile.objects.get(user=request.user)
        is_customer = user_profile and user_profile.customer is not None
        current_user_enable_confirm_jobs = user_profile.enable_confirm_jobs
        estimate_id = data.get('estimate_id')
        customer_purchase_order = data.get('customer_purchase_order')
        priority = data.get('priority', 'N')
        ident = data.get('ident')
        enable_flightaware_tracking = data.get('enable_flightaware_tracking', False)

        job_status = 'A'

        customer = None

        if is_customer:
            customer = user_profile.customer

            if current_user_enable_confirm_jobs:
                job_status = 'A'
            else:
                job_status = 'U'
        else:
            customer = Customer.objects.get(id=data['customer_id'])

        aircraft_type = get_object_or_404(AircraftType, pk=data['aircraft_type_id'])
        airport = get_object_or_404(Airport, pk=data['airport_id'])
        fbo = get_object_or_404(FBO, pk=data['fbo_id'])
        on_site = False
        
        if data['on_site'] == 'true':
            on_site = True
        
        if enable_flightaware_tracking == 'true':
            enable_flightaware_tracking = True
        else:
            enable_flightaware_tracking = False

        estimated_arrival_date = data['estimated_arrival_date']
        arrival_formatted_date = 'Not Specified'

        if estimated_arrival_date == 'null':
            estimated_arrival_date = None
            enable_flightaware_tracking = False
        else :
            # Remove the timezone name
            date_str_cleaned = estimated_arrival_date.split(' (')[0]

            # Define the format of the cleaned string
            date_format = "%a %b %d %Y %H:%M:%S GMT%z"

            dt = datetime.strptime(date_str_cleaned, date_format)
            
            arrival_formatted_date = dt.strftime("%m/%d/%y %H:%M") + " LT"

            try:
                timestamp = mktime_tz(parsedate_tz(estimated_arrival_date))
                # Now it is in UTC
                estimated_arrival_date = datetime(1970, 1, 1) + timedelta(seconds=timestamp)
            
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST)


        estimated_departure_date = data['estimated_departure_date']
        departure_formatted_date = 'Not Specified'

        if estimated_departure_date == 'null':
            estimated_departure_date = None
        else :
            # Remove the timezone name
            date_str_cleaned = estimated_departure_date.split(' (')[0]

            # Define the format of the cleaned string
            date_format = "%a %b %d %Y %H:%M:%S GMT%z"

            dt = datetime.strptime(date_str_cleaned, date_format)

            departure_formatted_date = dt.strftime("%m/%d/%y %H:%M") + " LT"

            try:
                timestamp = mktime_tz(parsedate_tz(estimated_departure_date))
                # Now it is in UTC
                estimated_departure_date = datetime(1970, 1, 1) + timedelta(seconds=timestamp)
            
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST)


        complete_by_date = data['complete_by_date']
        complete_before_formatted_date = 'Not Specified'

        if complete_by_date == 'null':
            complete_by_date = None
        else:
            # Remove the timezone name
            date_str_cleaned = complete_by_date.split(' (')[0]

            # Define the format of the cleaned string
            date_format = "%a %b %d %Y %H:%M:%S GMT%z"

            dt = datetime.strptime(date_str_cleaned, date_format)

            complete_before_formatted_date = dt.strftime("%m/%d/%y %H:%M") + " LT"

            try:
                timestamp = mktime_tz(parsedate_tz(complete_by_date))
                # Now it is in UTC
                complete_by_date = datetime(1970, 1, 1) + timedelta(seconds=timestamp)
            
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST)


        comment = data['comment']

        s = data['services']
        r = data['retainer_services']
        t = data['tags']
        follower_emails = data.get('follower_emails', None)
        services = []
        retainer_services = []
        tags = []
        job_follower_emails = []

        if s: 
            service_ids = data['services'].split(',')
            services = Service.objects.filter(id__in=service_ids)

        if r:
            retainer_service_ids = data['retainer_services'].split(',')
            retainer_services = RetainerService.objects.filter(id__in=retainer_service_ids)

        if t:
            tag_ids = data['tags'].split(',')
            tags = Tag.objects.filter(id__in=tag_ids)

        user = request.user

        newYorkTz = pytz.timezone("UTC") 

        # get today in newYorkTz
        today = datetime.now(newYorkTz).date()
        today_label = today.strftime("%Y%m%d")

        # Generate purchase order: current day + number of job received that day.
        #  So if today is 2019-01-01 and we have received 3 jobs today already, the purchase order will be 20190101-4
        jobs_created_today = Job.objects.filter(created_at__contains=today).count()

        purchase_order = today_label + '-' + str(jobs_created_today + 1)

        requested_by = data.get('requested_by', '')

        if requested_by == "":
            requested_by = None

        if on_site:
            arrival_formatted_date = 'On Site'

        job = Job(purchase_order=purchase_order,
                  customer=customer,
                  tailNumber=tailNumber,
                  aircraftType=aircraft_type,
                  airport=airport,
                  fbo=fbo,
                  estimatedETA=estimated_arrival_date,
                  estimatedETD=estimated_departure_date,
                  completeBy=complete_by_date,
                  created_by=user,
                  status=job_status,
                  requested_by=requested_by,
                  customer_purchase_order=customer_purchase_order,
                  on_site=on_site,
                  arrival_formatted_date=arrival_formatted_date,
                  departure_formatted_date=departure_formatted_date,
                  complete_before_formatted_date=complete_before_formatted_date,
                  enable_flightaware_tracking=enable_flightaware_tracking)

        job.save()

        # if ident is specified and it is not empty, then create a TailIdent entry or update the existing one by TailNumber
        if ident:
            ident = ident.strip()
            if ident:
                tail_ident = TailIdent.objects.filter(tail_number=tailNumber).first()
                if tail_ident:
                    tail_ident.ident = ident
                    tail_ident.save()
                else:
                    tail_ident = TailIdent(tail_number=tailNumber, ident=ident)
                    tail_ident.save()

        if follower_emails:
            job_follower_emails = follower_emails.split(',')
            for email in job_follower_emails:
                if not CustomerFollowerEmail.objects.filter(email=email, customer=customer).exists():
                    customer_follower_email = CustomerFollowerEmail(email=email, customer=customer)
                    customer_follower_email.save()

                job_follower_email = JobFollowerEmail(job=job, email=email)
                job_follower_email.save()
        else:
            if is_customer:
                # get all the customer persistent follower emails for this customer
                customer_follower_emails = CustomerFollowerEmail.objects.filter(customer=customer, is_persistent=True)
                for customer_follower_email in customer_follower_emails:
                    job_follower_email = JobFollowerEmail(job=job, email=customer_follower_email.email)
                    job_follower_email.save()


        for service in services:
            assignment = JobServiceAssignment(job=job,service=service)
            assignment.save()

        for retainer_service in retainer_services:
            assignment = JobRetainerServiceAssignment(job=job, retainer_service=retainer_service)
            assignment.save()

        for tag in tags:
            job_tag = JobTag(job=job, tag=tag)
            job_tag.save()

        if priority == 'H':
            try:
                priority_tag = Tag.objects.get(name='HIGH PRIORITY')
            except:
                priority_tag = Tag(name='HIGH PRIORITY', short_name='HIGH PRIORITY')
                priority_tag.save()

            job_tag = JobTag(job=job, tag=priority_tag)
            job_tag.save()

        # TODO: Calculate estimated completion time based on the estimated times of the selected services and aircraft type

        if comment:
            is_public = False

            if user.profile.customer:
                is_public = True

            job_comment = JobComments(job=job,
                                    comment=comment,
                                    is_public=is_public,
                                    author=user)
            job_comment.save()        

        
        name = job.tailNumber + '_' + job.airport.initials + '_' + datetime.today().strftime('%Y-%m-%d')
        counter = 0
        for photo in request.data.getlist('image'):
            name = name + '_' + str(counter)
            
            p = JobPhotos(job=job,
                          uploaded_by=request.user,
                          image=photo,
                          name=name,
                          customer_uploaded=True,
                          size=photo.size)
            p.save()


        # if the estimate is not null, then we need to update the estimate with the job id
        if estimate_id:
            estimate = JobEstimate.objects.get(id=estimate_id)
            estimate.job = job
            estimate.save()


        # after creating services calculate the job price
        # update price
        price_breakdown = PriceBreakdownService().get_price_breakdown(job)
        job.price = price_breakdown.get('totalPrice')
        job.travel_fees_amount_applied = price_breakdown.get('total_travel_fees_amount_applied')
        job.fbo_fees_amount_applied = price_breakdown.get('total_fbo_fees_amount_applied')
        job.vendor_higher_price_amount_applied = price_breakdown.get('total_vendor_higher_price_amount_applied')
        job.management_fees_amount_applied = price_breakdown.get('total_management_fees_amount_applied')

        job.save()

        # if user is customer, this is submitted, otherwise it is accepted
        JobStatusActivity.objects.create(job=job, user=request.user, status=job_status)

        # delete if tailaircraft lookup already exists, and create a new entry
        TailAircraftLookup.objects.filter(tail_number=job.tailNumber).delete()

        TailAircraftLookup.objects.create(tail_number=job.tailNumber, aircraft_type=job.aircraftType, customer=job.customer)


        # update the tail service lookup table
        # delete all tail service lookup entries for this tail number and then add them back
        TailServiceLookup.objects.filter(tail_number=job.tailNumber).delete()

        for service in services:
            TailServiceLookup.objects.create(tail_number=job.tailNumber, service=service, customer=job.customer)

        # delete all tail retainer service lookup entries for this tail number and then add them back
        TailRetainerServiceLookup.objects.filter(tail_number=job.tailNumber).delete()

        for retainer_service in retainer_services:
            TailRetainerServiceLookup.objects.create(tail_number=job.tailNumber, retainer_service=retainer_service, customer=job.customer)


        # if is_customer is True, send SMS and email to all admins and account managers
        if is_customer:
            try:
                vip_tag = Tag.objects.get(name='VIP')
            except:
                vip_tag = None
            
            if vip_tag:
                job_tag = JobTag(job=job, tag=vip_tag)
                job_tag.save()

            SMSNotificationService().send_create_job_notification(job, request.user)

            EmailNotificationService().send_create_job_notification(job, services, retainer_services, request.user)

            # AUTO ASSIGNMENT
            if customer.customer_settings.enable_auto_assignment \
                and not customer.customer_settings.enable_approval_process \
                and airport.preferred_project_manager:
                
                preferred_project_manager = airport.preferred_project_manager
                
                external_vendor = None
                if preferred_project_manager.profile.vendor \
                    and preferred_project_manager.profile.vendor.is_external:
                    external_vendor = preferred_project_manager.profile.vendor

                service_names = ''
                retainer_service_names = ''

                for assignment in job.job_service_assignments.all():
                    assignment.project_manager = preferred_project_manager
                    assignment.status = 'A'
                    assignment.vendor = external_vendor

                    assignment.save()

                    service_names += assignment.service.name + ', '

                for assignment in job.job_retainer_service_assignments.all():
                    assignment.project_manager = preferred_project_manager
                    assignment.status = 'A'
                    assignment.vendor = external_vendor

                    assignment.save()

                    retainer_service_names += assignment.retainer_service.name + ', '
                
                job.vendor = external_vendor
                job.status = 'S'
                job.save()
                
                # the user is null because the system is assigning the job
                JobStatusActivity.objects.create(job=job, status='S')

                if preferred_project_manager.profile.phone_number:
                    unique_phone_numbers = []
                    unique_phone_numbers.append(preferred_project_manager.profile.phone_number)
                    SMSNotificationService().send_job_assigned_notification(job, unique_phone_numbers)

                # if preferred_project_manager is enable_accept_jobs, then send the email notification
                if preferred_project_manager.profile.enable_accept_jobs:
                    unique_emails = []
                    if preferred_project_manager.profile.enable_accept_jobs:
                        if preferred_project_manager.email not in unique_emails:
                            unique_emails.append(preferred_project_manager.email)

                        additional_emails = UserEmail.objects.filter(user=preferred_project_manager)
                        for additional_email in additional_emails:
                            if additional_email.email not in unique_emails:
                                unique_emails.append(additional_email.email)

                    EmailNotificationService().send_job_assigned_notification(job, unique_emails, service_names, retainer_service_names)

                    LastProjectManagersNotified.objects.create(job=job, project_manager_id=preferred_project_manager.id)
                    JobAcceptanceNotification.objects.create(job=job, project_manager_id=preferred_project_manager.id, attempt=1)

                    thread1 = threading.Thread(target=self.schedule_acceptance_emails, args=(job.id,))
                    thread1.start()

        # if there is an estimate for this job, then you need to update the estimate status to accepted if it is in pending
        try:
            job_estimate = JobEstimate.objects.get(job=job)
        except:
            job_estimate = None

        if job_estimate:
            if job_estimate.status == 'P':
                job_estimate.status = 'A'
                job_estimate.save()


        response = {
            'id': job.id,
            'purchase_order': job.purchase_order
        }

        # send email to job followers if job_follower_emails is not empty
        if job_follower_emails:
            EmailNotificationService().send_create_job_notification_to_followers(job, services, retainer_services)

        return Response(response, status.HTTP_201_CREATED)



    def can_create_job(self, user):
        """
        Check if the user has permission to create a job.
        """
        # user customer can create a job
        user_profile = UserProfile.objects.get(user=user)
        is_customer = user_profile and user_profile.customer is not None

        if user.is_superuser \
                 or user.is_staff \
                 or is_customer \
                 or user.groups.filter(name='Account Managers').exists() \
                 or user.groups.filter(name='Internal Coordinators').exists():
            return True
        else:
            return False
        
    def schedule_acceptance_emails(self, job_id):
        EmailNotificationService().schedule_acceptance_emails(job_id)
