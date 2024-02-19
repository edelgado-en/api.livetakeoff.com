from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.serializers import TailAlertSerializer

from api.models import (TailAlert, Job)

class TailNoteLookupView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        job_id = request.data.get('jobId', None)

        job = get_object_or_404(Job, pk=job_id)

        # Fetcha tail alert for the tail number on the job that must have a notes specified. Notes cannot be empty
        #IGNORE CASE
        tail_alert = TailAlert.objects.filter(tailNumber__iexact=job.tailNumber, notes__isnull=False).first()

        if not tail_alert:
            # notes cannot be empty
            return Response({'error': 'No tail alert found for this tail number'}, status=status.HTTP_404_NOT_FOUND)
        
        # check if notes is empty
        if not tail_alert.notes:
            return Response({'error': 'No notes found for this tail number'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = TailAlertSerializer(tail_alert)

        return Response(serializer.data, status=status.HTTP_200_OK)
