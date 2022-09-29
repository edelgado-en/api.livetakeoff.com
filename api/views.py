from rest_framework import permissions
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
import os

class UserView(APIView):

    def get(self, request):
        print(os.environ.get('TEST'))
        qs = User.objects.all()
        return Response('hello')
