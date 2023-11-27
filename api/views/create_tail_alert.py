from django.db.models import Q
from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.response import Response

from rest_framework.parsers import MultiPartParser, FormParser

from api.models import (TailAlert, TailFile)

from api.serializers import TailAlertSerializer

class CreateTailAlertView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        if not self.can_create_alerts(request.user):
            return Response({'error': 'You do not have permission to create tail alerts'}, status=status.HTTP_403_FORBIDDEN)

        tail_number = request.data.get('tailNumber')
        message = request.data.get('message')
        notes = request.data.get('notes')

        file = request.data.get('file')
        is_public = request.data.get('is_public', False)

        if not tail_number or (not message and not notes):
            return Response({'error': 'You must provide a tail number and a message'}, status=status.HTTP_400_BAD_REQUEST)

        if TailAlert.objects.filter(tailNumber=tail_number).exists():
            return Response({'error': 'A tail details already exists for this tail number'}, status=status.HTTP_400_BAD_REQUEST)

        tail_alert = TailAlert.objects.create(tailNumber=tail_number,
                                              message=message,
                                              notes=notes,
                                              author=request.user)

        if file:
            TailFile.objects.create(tail_alert=tail_alert,
                                                file=file,
                                                uploaded_by=request.user,
                                                name=file.name,
                                                size=file.size,
                                                is_public=is_public)

        serializer = TailAlertSerializer(tail_alert)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def can_create_alerts(self, user):
        if user.is_superuser \
          or user.is_staff \
          or user.groups.filter(name='Account Managers').exists():
           return True

        return False
