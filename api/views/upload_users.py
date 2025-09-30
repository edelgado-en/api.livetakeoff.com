from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User

from api.models import (Customer, UserProfile)

class UploadUsersView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        users = self.request.data.get('users', [])
        # users is an array of objects with the following structure:
        #{
        #"first_name": "Daniel",
        #"last_name": "Ratliff",
        #"email": "daniel.ratliff@wheelsup.com"
        #}

        # iterate through users and create a new user for each one with the following password: LTOchangeme2025!
        # and set the following userProfile fields for all of them:
        # email_notifications = True
        # enable_email_notification_job_comment_added = True
        # is_job_submitter_only = True
        # avatar = 'https://res.cloudinary.com/datidxeqm/image/upload/v1/media/profiles/wheels_up_logo_nsgcoi_abwjn3'
        # customer = Search for the Customer with the name "Wheels Up"
        # 
        # If the user already exists (based on email), skip it and move to the next one.

        created_users = []
        skipped_users = []

        customer = get_object_or_404(Customer, name="Wheels Up")

        for user_data in users:
            email = user_data.get('email')
            first_name = user_data.get('first_name')
            last_name = user_data.get('last_name')

            if not email or not first_name or not last_name:
                skipped_users.append({'email': email, 'reason': 'Missing required fields'})
                continue

            if User.objects.filter(email=email).exists():
                skipped_users.append({'email': email, 'reason': 'User already exists'})
                continue

            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password='LTOchangeme2025!'
            )

            UserProfile.objects.create(
                user=user,
                customer=customer,
                email_notifications=True,
                enable_email_notification_job_comment_added=True,
            )

            created_users.append({'email': email, 'id': user.id})

        return Response({
            'created_users': created_users,
            'skipped_users': skipped_users
        }, status=status.HTTP_201_CREATED)
        
