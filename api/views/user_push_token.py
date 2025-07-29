from rest_framework import (permissions, status)
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

class UserPushTokenView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        token = request.data.get('expo_push_token')
        
        if token:
            profile = request.user.profile
            profile.expo_push_token = token
            profile.save()
            
            return Response({'status': 'token saved'})
        
        return Response({'error': 'No token provided'}, status=400)