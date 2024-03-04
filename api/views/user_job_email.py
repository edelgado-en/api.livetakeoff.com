from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User

from api.models import (Job, UserEmail)

class UserJobEmailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, job_id):
        job = Job.objects.get(pk=job_id)

        user = job.created_by

        emails = []

        email = user.email

        if email:
            emails.append({'id': user.id, 'email': email})

        user_emails = UserEmail.objects.filter(user=user).all()

        for user_email in user_emails:
            emails.append({'id': user_email.id, 'email': user_email.email})

        return Response({'emails': emails}, status=status.HTTP_200_OK)





    


    
    





