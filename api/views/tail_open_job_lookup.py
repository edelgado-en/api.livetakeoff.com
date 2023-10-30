from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.models import (
    Job
)

class TailOpenJobLookupView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, tailnumber):
        # only return 200 to avoid showing a 404 to the user
        try:
            # fetch a job that is open and has the tail number. An open job has a status or A, S, U, or W
            job = Job.objects.filter(tailNumber__iexact=tailnumber, status__in=['A', 'S', 'U', 'W']).first()

            if job:
                # return a data object with the job id and the tail number
                data = {
                    'jobId': job.id,
                    'tailNumber': job.tailNumber
                }
                return Response(data, status=status.HTTP_200_OK)
            else:
                return Response({'id': 0}, status=status.HTTP_200_OK)
        
        except Job.DoesNotExist:
            return Response({'id': 0}, status=status.HTTP_200_OK)