from rest_framework import serializers

from api.models import UserProfile

from api.serializers.vendor import VendorSerializer
from api.serializers.customer import CustomerSerializer

class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    vendor = VendorSerializer()
    customer = CustomerSerializer()

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'email_notifications',
            'sms_notifications',
            'inventory_email_notifications',
            'enable_email_notification_job_created',
            'enable_email_notification_scheduled_job_created',
            'enable_email_notification_job_completed',
            'enable_email_notification_job_accepted',
            'enable_email_notification_job_confirmed',
            'enable_email_notification_job_returned',
            'enable_email_notification_job_comment_added',
            'enable_email_notification_inventory_out_of_stock',
            'enable_email_notification_inventory_threshold_met',
            'enable_sms_notification_job_created',
            'enable_sms_notification_job_completed',
            'enable_sms_notification_job_started',
            'enable_sms_notification_job_cancelled',
            'show_airport_fees',
            'enable_confirm_jobs',
            'enable_accept_jobs',
            'enable_all_customers',
            'enable_all_airports',
            'enable_inventory_dashboard',
            'enable_estimates',
            'enable_invoice',
            'show_job_price',
            'master_vendor_pm',
            'prompt_requested_by',
            'location',
            'phone_number',
            'avatar',
            'about',
            'vendor',
            'customer',
            'is_job_submitter_only'
        ]