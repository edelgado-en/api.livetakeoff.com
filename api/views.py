from rest_framework import permissions
from django.contrib.auth.models import User
from .models import JobPhotos
from rest_framework.response import Response
from rest_framework.views import APIView
import os

class UserView(APIView):

    def get(self, request):
        photos = JobPhotos.objects.all()

        for photo in photos:
            print(photo.image.url)

        return Response('hello')
