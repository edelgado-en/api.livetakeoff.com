from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from django.contrib.auth.models import User

from api.serializers import UsersSerializer

from api.models import (UserEmail)


class UserDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        user = User.objects.select_related('profile').get(pk=id)

        emails = UserEmail.objects.filter(user=user)

        user.additional_emails = []

        if emails:
            email_array = []
            for email in emails:
                obj = {
                    'id': email.id,
                    'email': email.email
                }

                email_array.append(obj)

            user.additional_emails = email_array 

        serializer = UsersSerializer(user)
            
        return Response(serializer.data)
    

    def patch(self, request, id):
        user = User.objects.select_related('profile').get(pk=id)
        email = request.data.get('email', user.email)
        email_notifications = request.data.get('email_notifications', user.profile.email_notifications)
        sms_notifications = request.data.get('sms_notifications', user.profile.sms_notifications)
        enable_email_notification_job_created = request.data.get('enable_email_notification_job_created', user.profile.enable_email_notification_job_created)
        enable_email_notification_scheduled_job_created = request.data.get('enable_email_notification_scheduled_job_created', user.profile.enable_email_notification_scheduled_job_created)
        enable_email_notification_job_completed = request.data.get('enable_email_notification_job_completed', user.profile.enable_email_notification_job_completed)
        enable_email_notification_job_accepted = request.data.get('enable_email_notification_job_accepted', user.profile.enable_email_notification_job_accepted)
        enable_email_notification_job_confirmed = request.data.get('enable_email_notification_job_confirmed', user.profile.enable_email_notification_job_confirmed)
        enable_email_notification_job_returned = request.data.get('enable_email_notification_job_returned', user.profile.enable_email_notification_job_returned)
        enable_email_notification_job_comment_added = request.data.get('enable_email_notification_job_comment_added', user.profile.enable_email_notification_job_comment_added)
        enable_email_notification_inventory_out_of_stock = request.data.get('enable_email_notification_inventory_out_of_stock', user.profile.enable_email_notification_inventory_out_of_stock)
        enable_email_notification_inventory_threshold_met = request.data.get('enable_email_notification_inventory_threshold_met', user.profile.enable_email_notification_inventory_threshold_met)

        enable_sms_notification_job_created = request.data.get('enable_sms_notification_job_created', user.profile.enable_sms_notification_job_created)
        enable_sms_notification_job_completed = request.data.get('enable_sms_notification_job_completed', user.profile.enable_sms_notification_job_completed)
        enable_sms_notification_job_started = request.data.get('enable_sms_notification_job_started', user.profile.enable_sms_notification_job_started)
        enable_sms_notification_job_cancelled = request.data.get('enable_sms_notification_job_cancelled', user.profile.enable_sms_notification_job_cancelled)

        user.profile.enable_email_notification_job_created = enable_email_notification_job_created
        user.profile.enable_email_notification_scheduled_job_created = enable_email_notification_scheduled_job_created
        user.profile.enable_email_notification_job_completed = enable_email_notification_job_completed
        user.profile.enable_email_notification_job_accepted = enable_email_notification_job_accepted
        user.profile.enable_email_notification_job_confirmed = enable_email_notification_job_confirmed
        user.profile.enable_email_notification_job_returned = enable_email_notification_job_returned
        user.profile.enable_email_notification_job_comment_added = enable_email_notification_job_comment_added
        user.profile.enable_email_notification_inventory_out_of_stock = enable_email_notification_inventory_out_of_stock
        user.profile.enable_email_notification_inventory_threshold_met = enable_email_notification_inventory_threshold_met

        user.profile.enable_sms_notification_job_created = enable_sms_notification_job_created
        user.profile.enable_sms_notification_job_completed = enable_sms_notification_job_completed
        user.profile.enable_sms_notification_job_started = enable_sms_notification_job_started
        user.profile.enable_sms_notification_job_cancelled = enable_sms_notification_job_cancelled

        user.profile.email_notifications = email_notifications
        user.profile.sms_notifications = sms_notifications


        user.profile.show_airport_fees = request.data.get('show_airport_fees', user.profile.show_airport_fees)
        user.profile.show_job_price = request.data.get('show_job_price', user.profile.show_job_price)
        user.profile.enable_all_customers = request.data.get('enable_all_customers', user.profile.enable_all_customers)
        user.profile.enable_all_airports = request.data.get('enable_all_airports', user.profile.enable_all_airports)
        user.profile.enable_inventory_dashboard = request.data.get('enable_inventory_dashboard', user.profile.enable_inventory_dashboard)
        user.profile.enable_estimates = request.data.get('enable_estimates', user.profile.enable_estimates)
        user.profile.enable_accept_jobs = request.data.get('enable_accept_jobs', user.profile.enable_accept_jobs)
        user.profile.master_vendor_pm = request.data.get('master_vendor_pm', user.profile.master_vendor_pm)
        user.profile.enable_confirm_jobs = request.data.get('enable_confirm_jobs', user.profile.enable_confirm_jobs)
        user.profile.prompt_requested_by = request.data.get('prompt_requested_by', user.profile.prompt_requested_by)

        # if user.profile.email_notifications is false, then disabled all email notificaitons for this user
        if not email_notifications:
            user.profile.enable_email_notification_job_created = False
            user.profile.enable_email_notification_scheduled_job_created = False
            user.profile.enable_email_notification_job_completed = False
            user.profile.enable_email_notification_job_accepted = False
            user.profile.enable_email_notification_job_confirmed = False
            user.profile.enable_email_notification_job_returned = False
            user.profile.enable_email_notification_job_comment_added = False
            user.profile.enable_email_notification_inventory_out_of_stock = False
            user.profile.enable_email_notification_inventory_threshold_met = False

        if not sms_notifications:
            user.profile.enable_sms_notification_job_created = False
            user.profile.enable_sms_notification_job_completed = False
            user.profile.enable_sms_notification_job_started = False
            user.profile.enable_sms_notification_job_cancelled = False

        user.profile.save()

        user.email = email
        user.save()

        user.additional_emails = []

        serializer = UsersSerializer(user)

        return Response(serializer.data, status.HTTP_200_OK)
