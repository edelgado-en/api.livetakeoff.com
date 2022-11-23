from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from datetime import datetime

from api.models import (JobEstimate, JobEstimateDiscount, JobEstimateAdditionalFee)

from api.serializers import (JobEstimateDetailSerializer,)

from api.notification_util import NotificationUtil
from api.email_util import EmailUtil

class JobEstimateDetailView(APIView):
    permission_classes = (permissions.AllowAny,)


    def get(self, request, id):
        estimate = get_object_or_404(JobEstimate, pk=id)

        job_service_estimates = []
        for job_service_estimate in estimate.job_service_estimates.all():
            job_service_estimates.append({
                'id': job_service_estimate.id,
                'name': job_service_estimate.service.name,
                'price': job_service_estimate.price,
            })

        estimate.services = job_service_estimates

        serializer = JobEstimateDetailSerializer(estimate)

        return Response(serializer.data)


    def post(self, request, id):
        estimate = get_object_or_404(JobEstimate, pk=id)

        # if this estimate has been processed already, throw an error
        if estimate.is_processed:
            return Response({'error': 'This estimate has already been processed'}, status=status.HTTP_400_BAD_REQUEST)


        # update estimate status
        estimate.status = request.data.get('status')
        estimate.is_processed = True
        estimate.processed_at = datetime.now()
        
        estimate.save()

       # notify the user who requested the estimate via email and text message
        notification_util = NotificationUtil()

        # get the phone number of the user who requested the estimate
        phone_number = estimate.requested_by.profile.phone_number

        status_name = 'REJECTED'

        if estimate.status == 'A':
            status_name = 'ACCEPTED'

        if phone_number:
            # send a text message
            message = f'Your estimate for aircraft {estimate.aircraftType.name} at airport {estimate.airport.initials} has been {status_name}. You can checkout it out at https://livetakeoff.com/estimates/{estimate.id}'
            notification_util.send(message, phone_number.as_e164)

        
        # TODO: send an email
        # email_util = EmailUtil()


        return Response(status=status.HTTP_200_OK)