from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.models import (
    TailAlert
)

from api.serializers import (TailAlertSerializer)


class TailAlertLookupView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, tailnumber):
        # only return 200 to avoid showing a 404 to the user
        try:
            tailAlert = TailAlert.objects.filter(tailNumber__iexact=tailnumber).first()
            if tailAlert:
                serializer = TailAlertSerializer(tailAlert)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'id': 0}, status=status.HTTP_200_OK)
        
        except TailAlert.DoesNotExist:
            return Response({'id': 0}, status=status.HTTP_200_OK)
