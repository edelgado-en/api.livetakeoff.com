from rest_framework import (permissions, status)
from django.contrib.auth.models import User
from rest_framework.response import Response
from rest_framework.views import APIView

from ..models import (UserProfile, CustomerSettings)

from inventory.models import LocationUser

class UserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        user_profile = UserProfile.objects.get(user=user)

        avatar = None

        if user_profile and user_profile.avatar:
            avatar = user_profile.avatar.url

        customerName = None
        customerId = None

        canSeePrice = False

        canConfirmJobs = False

        canAcceptJobs = False

        canSeeAirportAdditionalFees = False

        customerLogo = None
        if user_profile and user_profile.customer and user_profile.customer.logo:
            customerLogo = user_profile.customer.logo.url

        if user_profile and user_profile.customer:
            customerName = user_profile.customer.name
            customerId = user_profile.customer.id

            if user_profile.customer.customer_settings.show_job_price:
                canSeePrice = user_profile.show_job_price

            if user_profile.enable_confirm_jobs:
                canConfirmJobs = user_profile.enable_confirm_jobs

        if user_profile and user_profile.show_airport_fees:
            canSeeAirportAdditionalFees = user_profile.show_airport_fees

        if user_profile and user_profile.enable_accept_jobs:
            canAcceptJobs = user_profile.enable_accept_jobs

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
        is_internal_coordinator = user.groups.filter(name='Internal Coordinators').exists()

        is_external_project_manager = is_project_manager and user_profile.vendor is not None and user_profile.vendor.is_external

        #a user is consider a customer when its profile has a reference to customer
        is_customer = user_profile and user_profile.customer is not None
        user.is_customer = is_customer

        # if user is customer and customer settings  has a retainer amount greater than zero, then the user is considered a Premium Member
        is_premium_member = False
        showSpendingInfo = False
        
        if is_customer:
            customer_settings = CustomerSettings.objects.get(customer=user_profile.customer)
            if customer_settings and customer_settings.retainer_amount and customer_settings.retainer_amount > 0:
                is_premium_member = True

            if customer_settings and customer_settings.show_spending_info:
                showSpendingInfo = True


        canSeeInventoryDashboard = False

        if user.is_superuser:
            access_level_label = 'Super User'
            canSeePrice = True
            showSpendingInfo = True

        elif user.is_staff:
            access_level_label = 'Admin'
            canSeePrice = True
            showSpendingInfo = True

        elif is_account_manager:
            access_level_label = 'Account Manager'
            canSeePrice = True
            showSpendingInfo = True

        elif is_customer:
            access_level_label = 'Customer'

        elif is_internal_coordinator:
            access_level_label = 'Internal Coordinator'
            canSeePrice = user_profile.show_job_price
            canSeeInventoryDashboard = user_profile.enable_inventory_dashboard

        elif is_project_manager:
            access_level_label = 'Project Manager'

        
        phone_number = ''
        if user_profile.phone_number:
            phone_number = user_profile.phone_number.as_e164

        #showInventory should be true if the user has at leat one entry in LocationUser or if the user isAdmin, isSuperUser or isAccountManager
        showInventory = False
        if user.is_superuser or user.is_staff or user.groups.filter(name='Account Managers').exists():
            showInventory = True
        else:
            if LocationUser.objects.filter(user=user).exists():
                showInventory = True
        
        content = {
            "initials": first_name[0] + last_name[0],
            "about": user_profile.about,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": phone_number,
            "isProjectManager": is_project_manager,
            "isExternalProjectManager": is_external_project_manager,
            "isAccountManager": is_account_manager,
            "isInternalCoordinator": is_internal_coordinator,
            "isAdmin": user.is_staff,
            "isSuperUser": user.is_superuser,
            "isCustomer": user.is_customer,
            "fullName": first_name + ' ' + last_name,
            "access_level_label": access_level_label,
            "avatar": avatar,
            "customerLogo": customerLogo,
            "customerName": customerName,
            "customerId": customerId,
            "isPremiumMember": is_premium_member,
            "canSeePrice": canSeePrice,
            'canConfirmJobs': canConfirmJobs,
            'canAcceptJobs': canAcceptJobs,
            "canSeeInventoryDashboard": canSeeInventoryDashboard,
            "receive_sms_notifications": user_profile.sms_notifications,
            "receive_email_notifications": user_profile.email_notifications,
            'showSpendingInfo': showSpendingInfo,
            'enableEstimates': user_profile.enable_estimates,
            'enableInvoices': user_profile.enable_invoice,
            'promptRequestedBy': user_profile.prompt_requested_by,
            'showInventory': showInventory,
            'showAirportFees': canSeeAirportAdditionalFees
        }

        return Response(content)

    def patch(self, request):
        user = User.objects.get(id=request.user.id)
        user_profile = UserProfile.objects.get(user=user)

        user_profile.about = request.data['about']
        user_profile.email_notifications = request.data['email_notifications']
        user_profile.sms_notifications = request.data['sms_notifications']
        user_profile.phone_number = request.data.get('phone_number', None)

        user_profile.save()

        user.username = request.data['username']
        user.first_name = request.data['first_name']
        user.last_name = request.data['last_name']
        user.email = request.data['email']

        user.save()

        return Response(status.HTTP_200_OK)