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
        JobTag
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

        # if user is customer, get customer from user profile
        user_profile = UserProfile.objects.get(user=request.user)
        is_customer = user_profile and user_profile.customer is not None
        estimate_id = data.get('estimate_id')

        job_status = 'A'

        if is_customer:
            customer = user_profile.customer
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
                  on_site=on_site)

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
            job_comment = JobComments(job=job,
                                    comment=comment,
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
            # send SMS to all admins and account managers
            notification_util = NotificationUtil()

            # the link is throwing a 30007 error in Twilio
            #message = f'Customer {job.customer.name} has submitted job {job.purchase_order} for Tail number {job.tailNumber}. Check it out at  http://livetakeoff.com/jobs/{job.id}/details'
            message = f'Customer {job.customer.name} has submitted job {job.purchase_order} for Tail number {job.tailNumber}'

            admins = User.objects.filter(Q(is_superuser=True) | Q(is_staff=True) | Q(groups__name='Account Managers'))

            unique_phone_numbers = []

            for user in admins:
                if user.profile.phone_number:
                    if user.profile.phone_number not in unique_phone_numbers:
                        unique_phone_numbers.append(user.profile.phone_number)


            for phone_number in unique_phone_numbers:
                notification_util.send(message, phone_number.as_e164)

            # send email to all admins and account managers
            subject = f'Customer {job.customer.name} has submitted a job'

            body = f'''
                    <div style="text-align: center; font-size: 20px; font-weight: bold; margin-bottom: 20px;">Customer Job Request</div>
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
                    </table>
                    <div style="margin-top:20px;padding:5px;font-weight: 700;">Check it out at</div>
                    <div style="padding:5px">http://livetakeoff.com/jobs/{job.id}/details</div>
                    '''

            email_util = EmailUtil()
            email_util.send_email('rob@cleantakeoff.com', subject, body)
        
        
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
