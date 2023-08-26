import pdb
from django.http import FileResponse, HttpResponse
from rest_framework .response import Response
from rest_framework import (permissions, status)
import io


from rest_framework.views import APIView


import time


from api.models import (Job, JobPhotos, JobServiceAssignment, JobRetainerServiceAssignment)

class JobCloseoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request, id):
        if not self.can_closeout_job(request.user):
            return Response({'error': 'You do not have permission to view close out job'}, status=status.HTTP_403_FORBIDDEN)

        

        
    def can_closeout_job(self, user):
        if user.is_superuser \
          or user.is_staff \
          or user.groups.filter(name='Account Managers').exists():
           return True
        
        return False

