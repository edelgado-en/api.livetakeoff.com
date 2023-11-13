from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from datetime import datetime

import base64

from api.models import (JobEstimate, JobEstimateDiscount, JobEstimateAdditionalFee)

from api.serializers import (JobEstimateDetailSerializer,)

from api.notification_util import NotificationUtil
from api.email_util import EmailUtil


class SharedJobEstimateDetailView(APIView):
    permission_classes = (permissions.AllowAny,)


    def get(self, request, encoded_id):
        # Base64 DECODE
        base64_bytes = encoded_id.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        message = message_bytes.decode('ascii')

        # split message with delimiter - and get the first part
        estimate_id = int(message.split('-')[0])

        estimate = get_object_or_404(JobEstimate, pk=estimate_id)

        job_service_estimates = []
        for job_service_estimate in estimate.job_service_estimates.all():
            job_service_estimates.append({
                'id': job_service_estimate.id,
                'name': job_service_estimate.service.name,
                'price': job_service_estimate.price,
                'category': job_service_estimate.service.category
            })

        estimate.services = job_service_estimates


        # Base64 ENCODE
        message = str(estimate.id) + '-' + estimate.tailNumber
        message_bytes = message.encode('ascii')
        base64_bytes = base64.b64encode(message_bytes)
        encoded_id = base64_bytes.decode('ascii')

        estimate.encoded_id = encoded_id

        serializer = JobEstimateDetailSerializer(estimate)

        return Response(serializer.data)


    def post(self, request, encoded_id):
         # Base64 DECODE
        base64_bytes = encoded_id.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        decoded_id = message_bytes.decode('ascii')

        # split message with delimiter - and get the first part
        estimate_id = int(decoded_id.split('-')[0])

        estimate = get_object_or_404(JobEstimate, pk=estimate_id)

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
            
            #Adding a link is throwing a 30007 error in Twilio
            #message = f'Your estimate for tail {estimate.tailNumber} at airport {estimate.airport.initials} has been {status_name}. You can checkout it out at https://livetakeoff.com/estimates/{estimate.id}'

            message = f'Your estimate for tail {estimate.tailNumber} at airport {estimate.airport.initials} has been {status_name}.'
            
            notification_util.send(message, phone_number.as_e164)



        return Response(status=status.HTTP_200_OK)