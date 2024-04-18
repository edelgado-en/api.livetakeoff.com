from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from datetime import (date, datetime, timedelta)
import pytz
from email.utils import parsedate_tz, mktime_tz

from django.contrib.auth.models import User

import base64

from api.pricebreakdown_service import PriceBreakdownService

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
        UserEmail
    )

from api.notification_util import NotificationUtil
from api.email_util import EmailUtil

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
        enable_confirm_jobs = user_profile.enable_confirm_jobs
        estimate_id = data.get('estimate_id')
        customer_purchase_order = data.get('customer_purchase_order')

        job_status = 'A'

        if is_customer:
            customer = user_profile.customer

            if enable_confirm_jobs:
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
        

        estimated_arrival_date = data['estimated_arrival_date']
        if estimated_arrival_date == 'null':
            estimated_arrival_date = None
        else :
            try:
                timestamp = mktime_tz(parsedate_tz(estimated_arrival_date))
                # Now it is in UTC
                estimated_arrival_date = datetime(1970, 1, 1) + timedelta(seconds=timestamp)
            
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST)


        estimated_departure_date = data['estimated_departure_date']
        if estimated_departure_date == 'null':
            estimated_departure_date = None
        else :
            try:
                timestamp = mktime_tz(parsedate_tz(estimated_departure_date))
                # Now it is in UTC
                estimated_departure_date = datetime(1970, 1, 1) + timedelta(seconds=timestamp)
            
            except ValueError:
                return Response(status=status.HTTP_400_BAD_REQUEST)


        complete_by_date = data['complete_by_date']
        if complete_by_date == 'null':
            complete_by_date = None
        else:
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
        services = []
        retainer_services = []
        tags = []

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

        arrival_formatted_date = 'Not Specified'
        if estimated_arrival_date:
            arrival_formatted_date = estimated_arrival_date.strftime('%m/%d/%y %H:%M')
            arrival_formatted_date += ' LT'

        if on_site:
            arrival_formatted_date = 'On Site'

        departure_formatted_date = 'Not Specified'
        if estimated_departure_date:
            departure_formatted_date = estimated_departure_date.strftime('%m/%d/%y %H:%M')
            departure_formatted_date += ' LT'

        complete_before_formatted_date = 'Not Specified'
        if complete_by_date:
            complete_before_formatted_date = complete_by_date.strftime('%m/%d/%y %H:%M')
            complete_before_formatted_date += ' LT'

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
                  complete_before_formatted_date=complete_before_formatted_date)

        job.save()


        for service in services:
            assignment = JobServiceAssignment(job=job,service=service)
            assignment.save()

        for retainer_service in retainer_services:
            assignment = JobRetainerServiceAssignment(job=job, retainer_service=retainer_service)
            assignment.save()

        for tag in tags:
            job_tag = JobTag(job=job, tag=tag)
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
        if is_customer and not enable_confirm_jobs:
            # send SMS to all admins and account managers
            notification_util = NotificationUtil()

            # the link is throwing a 30007 error in Twilio
            #message = f'Customer {job.customer.name} has submitted job {job.purchase_order} for Tail number {job.tailNumber}. Check it out at  http://livetakeoff.com/jobs/{job.id}/details'

            # the message needs to look like this:
            #JOB SUBMITTED
            #•⁠  ⁠Fly Alliance
            #•⁠  ⁠MIA
            #•⁠  ⁠N1122AA
            #ETA: On Site
            #ETD: 2/4/24 13:00
            
            # where Fly Alliance is the job.customer.name
            # MIA is the job.airport.initials
            # N1122AA is the job.tailNumber
            # ETA: On Site is the job.on_site
            # ETD: 2/4/24 13:00 is the job.estimatedETD

            # format job.estimatedETD to look like 2/4/24 13:00 and if it is none, then just put 'Not Specified'
            etd = 'Not Specified'
            if job.estimatedETD:
                etd = job.estimatedETD.strftime('%m/%d/%y %H:%M')

            eta = 'Not Specified'
            if job.estimatedETA:
                eta = job.estimatedETA.strftime('%m/%d/%y %H:%M')
            
            complete_before = 'Not Specified'
            if job.completeBy:
                complete_before = job.completeBy.strftime('%m/%d/%y %H:%M')

            if job.on_site:
                eta = 'On Site'

            message = f'JOB SUBMITTED\n•⁠  ⁠{job.customer.name}\n•⁠  ⁠{job.airport.initials}\n•⁠  ⁠{job.tailNumber}\nETA: {eta}\nETD: {etd}'

            admins = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True) | Q(groups__name='Account Managers'))

            unique_phone_numbers = []
            emails = []

            # Fetch all emails from customer users that belong to this customer that have enable_confirmed_jobs
            # set to True excluding the current user
            customer_users = UserProfile.objects.filter(customer=job.customer, enable_confirm_jobs=True).exclude(user=request.user)

            for customer_user in customer_users:
                if customer_user.user.email:
                    if customer_user.user.email not in emails:
                        emails.append(customer_user.user.email)

                additional_emails = UserEmail.objects.filter(user=customer_user.user)
                for additional_email in additional_emails:
                    if additional_email.email not in emails:
                        emails.append(additional_email.email)

                if customer_user.phone_number:
                    if customer_user.phone_number not in unique_phone_numbers:
                        unique_phone_numbers.append(customer_user.phone_number)

            for user in admins:
                if user.email:
                    if user.email not in emails:
                        emails.append(user.email)

                additional_emails = UserEmail.objects.filter(user=user)
                for additional_email in additional_emails:
                    if additional_email.email not in emails:
                        emails.append(additional_email.email)

                if user.profile.phone_number:
                    if user.profile.phone_number not in unique_phone_numbers:
                        unique_phone_numbers.append(user.profile.phone_number)


            for phone_number in unique_phone_numbers:
                notification_util.send(message, phone_number.as_e164)

            # send email to all admins and account managers
            subject = f'{job.tailNumber} - Job SUBMITTED by {job.customer.name}'

            service_names = ''
            for service in services:
                service_names += service.name + ', '

            # remove the last comma from service_names if not empty
            if service_names:
                service_names = service_names[:-2]

            retainer_service_names = ''
            for retainer_service in retainer_services:
                retainer_service_names += retainer_service.name + ', '

            # remove the last comma from retainer_service_names if not empty
            if retainer_service_names:
                retainer_service_names = retainer_service_names[:-2]

            message = str(job.id) + '-' + job.tailNumber
            message_bytes = message.encode('ascii')
            base64_bytes = base64.b64encode(message_bytes)
            base64_message = base64_bytes.decode('ascii')

            body = f'''
                    <div style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">Customer Job Request</div>
                    <a href="http://livetakeoff.com/shared/jobs/{base64_message}/confirm" style="display: inline-block; padding: 0.5625rem 1.125rem; margin: 0 5px; font-size: 1.5rem; font-weight: 400; line-height: 1.5; text-align: center; vertical-align: middle; cursor: pointer; border: 1px solid transparent; border-radius: 0.375rem; transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out; text-decoration: none; color: #fff; background-color: #007bff; border-color: #007bff;">CONFIRM</a>
                    <a href="http://livetakeoff.com/jobs/{job.id}/details" style="display: inline-block; padding: 0.5625rem 1.125rem; margin: 0 5px; font-size: 1.5rem; font-weight: 400; line-height: 1.5; text-align: center; vertical-align: middle; cursor: pointer; border: 1px solid transparent; border-radius: 0.375rem; transition: color 0.15s ease-in-out, background-color 0.15s ease-in-out, border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out; text-decoration: none; color: #212529; background-color: #f8f9fa; border-color: #f8f9fa;">EDIT</a>

                    <div style="margin-bottom:20px"></div>
                    <table style="border-collapse: collapse">
                        <tr>
                            <td style="padding:15px">Customer</td>
                            <td style="padding:15px">{job.customer.name}</td>
                        </tr>
                        <tr>
                            <td style="padding:15px">Job PO</td>
                            <td style="padding:15px">{job.purchase_order}</td>
                        </tr>
                        <tr>
                            <td style="padding:15px">Tail</td>
                            <td style="padding:15px">{job.tailNumber}</td>
                        </tr>
                        <tr>
                            <td style="padding:15px">Airport</td>
                            <td style="padding:15px">{job.airport.name}</td>
                        </tr>
                        <tr>
                            <td style="padding:15px">FBO</td>
                            <td style="padding:15px">{job.fbo.name}</td>
                        </tr>
                        <tr>
                            <td style="padding:15px">Arrival</td>
                            <td style="padding:15px">{eta}</td>
                        </tr>
                        <tr>
                            <td style="padding:15px">Departure</td>
                            <td style="padding:15px">{etd}</td>
                        </tr>
                        <tr>
                            <td style="padding:15px">Complete Before</td>
                            <td style="padding:15px">{complete_before}</td>
                        </tr>
                        <tr>
                            <td style="padding:15px">Services</td>
                            <td style="padding:15px">{service_names}</td>
                        </tr>
                        <tr>
                            <td style="padding:15px">Retainer Services</td>
                            <td style="padding:15px">{retainer_service_names}</td>
                        </tr>
                    </table>
                    <div style="margin-top:20px;padding:5px;font-weight: 700;"></div>
                    
                    '''

            email_util = EmailUtil()

            body += email_util.getEmailSignature()

            for email in emails:
                email_util.send_email(email, subject, body)
        
            # Fetch a Tag with the name VIP and create a JobTag for this job
            try:
                vip_tag = Tag.objects.get(name='VIP')
            except:
                vip_tag = None
            
            if vip_tag:
                job_tag = JobTag(job=job, tag=vip_tag)
                job_tag.save()

        
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
