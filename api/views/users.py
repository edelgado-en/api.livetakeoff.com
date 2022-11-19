from rest_framework import (permissions, status)
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import (UserProfile, CustomerSettings)

class UserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        user_profile = UserProfile.objects.get(user=user)

        avatar = None

        if user_profile and user_profile.avatar:
            avatar = user_profile.avatar.url

        customerName = None

        customerLogo = None
        if user_profile and user_profile.customer and user_profile.customer.logo:
            customerLogo = user_profile.customer.logo.url

        if user_profile and user_profile.customer:
            customerName = user_profile.customer.name


        first_name = ''
        last_name = ''

        if not user.first_name:
            first_name = user.username
        else:
            first_name = user.first_name

        if not user.last_name:
            last_name = user.username
        else:
            last_name = user.last_name

        access_level_label = 'Not Specified'

        is_project_manager = user.groups.filter(name='Project Managers').exists()
        is_account_manager = user.groups.filter(name='Account Managers').exists()

        #a user is consider a customer when its profile has a reference to customer
        is_customer = user_profile and user_profile.customer is not None
        user.is_customer = is_customer

        # if user is customer and customer settings  has a retainer amount greater than zero, then the user is considered a Premium Member
        is_premium_member = False
        if is_customer:
            customer_settings = CustomerSettings.objects.get(customer=user_profile.customer)
            if customer_settings and customer_settings.retainer_amount and customer_settings.retainer_amount > 0:
                is_premium_member = True


        if user.is_superuser:
            access_level_label = 'Super User'

        elif user.is_staff:
            access_level_label = 'Admin'

        elif is_account_manager:
            access_level_label = 'Account Manager'

        elif is_project_manager:
            access_level_label = 'Project Manager'

        elif is_customer:
            access_level_label = 'Customer'


        content = {
            "initials": first_name[0] + last_name[0],
            "about": user_profile.about,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "isProjectManager": is_project_manager,
            "isAccountManager": is_account_manager,
            "isAdmin": user.is_staff,
            "isSuperUser": user.is_superuser,
            "isCustomer": user.is_customer,
            "fullName": first_name + ' ' + last_name,
            "access_level_label": access_level_label,
            "avatar": avatar,
            "customerLogo": customerLogo,
            "customerName": customerName,
            "isPremiumMember": is_premium_member
        }

        return Response(content)

    def patch(self, request):
        user = User.objects.get(id=request.user.id)
        user_profile = UserProfile.objects.get(user=user)

        user_profile.about = request.data['about']
        user_profile.save()

        user.username = request.data['username']
        user.first_name = request.data['first_name']
        user.last_name = request.data['last_name']
        user.email = request.data['email']

        user.save()

        return Response(status.HTTP_200_OK)