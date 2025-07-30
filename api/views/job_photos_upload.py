import os
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions,status)
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response

from datetime import datetime

from ..models import (
        JobPhotos,
        Job,
        JobServiceAssignment,
        JobStatusActivity,
        JobRetainerServiceAssignment)
from ..serializers import JobPhotoSerializer

TOTAL_PHOTOS_MAX_COUNT = 10

class JobPhotosUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = JobPhotoSerializer
    lookup_url_kwarg = "jobid"

    def post(self, request, *args, **kwargs):
        jobid = self.kwargs.get(self.lookup_url_kwarg)
        job = get_object_or_404(Job, pk=jobid)

        is_interior = request.data.get('is_interior')
        is_exterior = request.data.get('is_exterior')
        is_customer = request.data.get('is_customer')
        
        interior = False
        customer = False
        
        if (is_interior == 'true'):
            interior = True

        if (is_exterior == 'true'):
            interior = False
        
        if (is_customer == 'true'):
            customer = True
        

        total_photos = JobPhotos.objects.filter(job=jobid, interior=interior, customer_uploaded=customer).count()

        # check if the total photos plus the new ones is greater than the max
        """ if total_photos + len(request.data.getlist('photo')) > TOTAL_PHOTOS_MAX_COUNT:
            return Response({'error': 'There is aleady 10 photos associated with this job'}, status=status.HTTP_406_NOT_ACCEPTABLE) """

        counter = 0

        name = job.tailNumber + '_' + job.airport.initials + '_' + datetime.today().strftime('%Y-%m-%d')

        for photo in request.data.getlist('photo'):
            file_name, file_extension = os.path.splitext(photo.name)
            
            filename = name + '_' + str(counter) + file_extension

            photo._name = filename
            
            p = JobPhotos(job=job,
                          uploaded_by=request.user,
                          image=photo,
                          name=filename,
                          size=photo.size,
                          interior=interior,
                          customer_uploaded=customer)
            p.save()

            counter = counter + 1


        JobStatusActivity.objects.create(job=job, user=request.user,
                                    status=job.status, activity_type='U')

        return Response({'uploaded_photos': counter}, status=status.HTTP_201_CREATED)

