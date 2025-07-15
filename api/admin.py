from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from api.models import (
    Service,
    ServiceType,
    RetainerService,
    ChecklistAction,
    Customer,
    CustomerSettings,
    CustomerAdmin as CustomerAssignedAdmin,
    AircraftType,
    Airport,
    FBO,
    Job,
    JobPhotos,
    JobComments,
    Vendor,
    VendorFile,
    UserProfile,
    CustomerProjectManager,
    CustomerDiscount,
    CustomerDiscountService,
    CustomerDiscountAirport,
    CustomerAdditionalFee,
    CustomerAdditionalFeeAirport,
    CustomerAdditionalFeeFBO,
    CustomerRetainerService,
    CustomerService,
    PriceList,
    PriceListEntries,
    EstimatedServiceTime,
    JobStatusActivity,
    JobServiceAssignment,
    JobRetainerServiceAssignment,
    Tag,
    JobEstimate,
    JobServiceEstimate,
    ServiceActivity,
    UserEmail,
    JobFiles,
    JobSchedule,
    TailAlert,
    LastProjectManagersNotified,
    JobAcceptanceNotification,
    Help,
    VendorCustomerPriceList,
    CustomerFollowerEmail,
    JobFollowerEmail,
    TailIdent,
    RetainerServiceActivity,
    CustomerTail,
    TailAircraftLookup
)

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False


class UserAdmin(BaseUserAdmin):
    inlines = [UserProfileInline]

admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'active', 'public', 'type', 'category', 'is_special', 'is_exterior_detail_level_1', 'is_exterior_detail_level_2', 'is_interior_detail_level_1', 'is_interior_detail_level_2']
    list_per_page = 100
    ordering = ['name', 'active']
    search_fields = ['name', 'active']

    def has_delete_permission(self, request, obj=None):
        # Disable delete because when you want to stop using a service, just set it to inactive
        return False

@admin.register(UserEmail)
class UserEmailAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'email']
    list_per_page = 100

    def has_delete_permission(self, request, obj=None):
        # Disable delete because when you want to stop using a service, just set it to inactive
        return False

@admin.register(ServiceType)
class ServicTypeeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'active']
    list_per_page = 100
    ordering = ['name', 'active']
    search_fields = ['name', 'active']

    def has_delete_permission(self, request, obj=None):
        # Disable delete because when you want to stop using a service, just set it to inactive
        return False


@admin.register(RetainerService)
class RetainerServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'active', 'category', 'is_special']
    list_per_page = 100
    ordering = ['name', 'active']
    search_fields = ['name', 'active']

    def has_delete_permission(self, request, obj=None):
        # Disable delete because when you want to stop using a service, just set it to inactive
        return False
    
@admin.register(ServiceActivity)
class ServiceActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'timestamp', 'job', 'service', 'price']
    list_per_page = 100
    ordering = ['timestamp']


@admin.register(ChecklistAction)
class ChecklistActionAdmin(admin.ModelAdmin):
    list_display = ['name', 'active']
    list_per_page = 100
    ordering = ['name', 'active']
    search_fields = ['name', 'active']

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'logo', 'banner', 'about', 'contact',  'phone_number', 'billingAddress', 'emailAddress', 'billingInfo', 'active', 'exterior_service_checker']
    list_per_page = 100
    ordering = ['name', 'emailAddress']
    search_fields = ['name', 'emailAddress']

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(CustomerAssignedAdmin)
class CustomerAssignedAdmins(admin.ModelAdmin):
    list_display = ['customer_setting', 'admin']
    list_per_page = 100


@admin.register(CustomerProjectManager)
class CustomerPMAdmin(admin.ModelAdmin):
    list_display = ['customer_setting', 'project_manager']
    list_per_page = 100


@admin.register(CustomerSettings)
class CustomerSettingsAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'show_spending_info', 'allow_cancel_job', 'retainer_amount', 'special_instructions', 'price_list', 'enable_flight_based_scheduled_cleaning']
    list_per_page = 100

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(CustomerDiscount)
class CustomerDiscountAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_setting', 'discount', 'type', 'percentage']


@admin.register(CustomerDiscountService)
class CustomerDiscountServiceAdmin(admin.ModelAdmin):
    list_display = ['customer_discount', 'service']


@admin.register(CustomerDiscountAirport)
class CustomerDiscountAirport(admin.ModelAdmin):
    list_display = ['customer_discount', 'airport']


@admin.register(CustomerAdditionalFee)
class CustomerAdditionalFeeAdmin(admin.ModelAdmin):
    list_display = ['customer_setting', 'type', 'fee', 'percentage']


@admin.register(CustomerAdditionalFeeFBO)
class CustomerAdditionalFeeFBOAdmin(admin.ModelAdmin):
    list_display = ['customer_additional_fee', 'fbo']


@admin.register(CustomerAdditionalFeeAirport)
class CustomerAdditionalFeeAirportAdmin(admin.ModelAdmin):
    list_display = ['customer_additional_fee', 'airport']


@admin.register(CustomerRetainerService)
class CustomerRetainerServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'retainer_service']

@admin.register(CustomerService)
class CustomerServiceAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'service']

@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'is_vendor']


@admin.register(PriceListEntries)
class PriceListEntriesAdmin(admin.ModelAdmin):
    list_display = ['id', 'price_list', 'aircraft_type', 'service', 'price']
    search_fields = ['aircraft_type', 'service']


@admin.register(EstimatedServiceTime)
class EstimatedServiceTimeAdmin(admin.ModelAdmin):
    list_display = ['id', 'service', 'aircraft_type', 'estimated_time']
    search_fields = ['aircraft_type', 'service']
    list_per_page = 100



@admin.register(AircraftType)
class AircraftTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'active']
    list_per_page = 100
    ordering = ['name', 'active']
    search_fields = ['name', 'active']

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ['initials', 'name', 'active', 'public', 'airport_type', 'preferred_project_manager', 'fee', 'fee_percentage']
    list_per_page = 100
    ordering = ['initials', 'name', 'active']
    search_fields = ['initials', 'name', 'active']

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(FBO)
class FBOAdmin(admin.ModelAdmin):
    list_display = ['name', 'active', 'public', 'hours_of_operation', 'fee', 'fee_percentage']
    list_per_page = 100 
    ordering = ['name', 'active']
    search_fields = ['name', 'active']

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'purchase_order', 'customer', 'requestDate', 'tailNumber', 'aircraftType', 'airport', 'fbo', 'estimatedETA', 'estimatedETD', 'completeBy', 'status', 'estimated_completion_time', 'actual_completion_time', 'price', 'hours_worked', 'minutes_worked', 'number_of_workers', 'vendor', 'vendor_charge', 'vendor_additional_cost', 'internal_additional_cost', 'subcontractor_profit', 'travel_fees_amount_applied', 'fbo_fees_amount_applied', 'vendor_higher_price_amount_applied', 'management_fees_amount_applied', 'enable_flightaware_tracking']
    list_per_page = 100
    ordering = ['created_at', 'purchase_order', 'customer', 'aircraftType', 'tailNumber', 'airport', 'fbo', 'status', 'completeBy']
    search_fields = ['tailNumber']

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(JobSchedule)
class JobScheduleAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'tailNumber', 'aircraftType', 'airport', 'fbo', 'start_date', 'repeat_every', 'is_recurrent', 'last_job_created_at', 'comment', 'created_by', 'created_at', 'is_deleted']
    list_per_page = 100


@admin.register(JobStatusActivity)
class JobStatusActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'timestamp', 'activity_type', 'status', 'job', 'user']
    list_per_page = 100
    ordering = ['timestamp']
    search_fields = ['status']


@admin.register(JobPhotos)
class JobPhotosAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'uploaded_by', 'job', 'name', 'image', 'size', 'interior']
    list_per_page = 100
    ordering = ['id', 'name']
    search_fields = ['id', 'job', 'name']

    def image_preview(self, obj):
        return obj.image_preview

    image_preview.short_description = 'Photo Preview'
    image_preview.allow_tags = True

@admin.register(JobFiles)
class JobFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'uploaded_by', 'job', 'name', 'file', 'size', 'customer_uploaded', 'is_public', 'is_customer_only']
    list_per_page = 100


@admin.register(JobComments)
class JobCommentsAdmin(admin.ModelAdmin):
    list_display = ['id', 'comment', 'author', 'job']
    list_per_page = 100
    search_fields = ['comment']


@admin.register(JobServiceAssignment)
class JobServiceAssignmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'job', 'service', 'status', 'project_manager', 'created_at', 'updated_at']
    list_per_page = 100
    ordering = ['created_at', 'updated_at']
    search_fields = ['job', 'service', 'project_manager']


@admin.register(JobRetainerServiceAssignment)
class JobRetainerServiceAssignmentAdmin(admin.ModelAdmin):
    list_display = ['id', 'job', 'retainer_service', 'status', 'project_manager', 'created_at', 'updated_at']
    list_per_page = 100
    ordering = ['created_at', 'updated_at']
    search_fields = ['job', 'service', 'project_manager']


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','billing_address', 'emails', 'phone_numbers', 'logo', 'notes', 'active', 'is_external']
    list_per_page = 100
    search_fields = ['name']

@admin.register(VendorFile)
class VendorFileAdmin(admin.ModelAdmin):
    list_display = ['id', 'vendor', 'name', 'file', 'file_type', 'is_expired', 'is_approved', 'expiration_date', 'created_at', 'uploaded_by', 'size']
    list_per_page = 100


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'short_name', 'description', 'color']
    list_per_page = 100
    search_fields = ['name']

@admin.register(JobEstimate)
class JobEstimateAdmin(admin.ModelAdmin):
    list_display = ['id', 'job', 'tailNumber', 'services_price', 'discounted_price', 'total_price']
    list_per_page = 100

@admin.register(JobServiceEstimate)
class JobServiceEstimateAdmin(admin.ModelAdmin):
    list_display = ['id', 'job_estimate', 'service', 'price']
    list_per_page = 100

@admin.register(TailAlert)
class TailAlertAdmin(admin.ModelAdmin):
    list_display = ['id', 'tailNumber', 'message', 'notes', 'author']
    list_per_page = 100
    search_fields = ['tailNumber']

@admin.register(LastProjectManagersNotified)
class LastProjectManagersNotifiedAdmin(admin.ModelAdmin):
    list_display = ['id', 'job', 'project_manager']
    list_per_page = 100
    search_fields = ['job']

@admin.register(JobAcceptanceNotification)
class JobAcceptanceNotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'job', 'project_manager', 'attempt', 'timestamp']
    list_per_page = 100
    search_fields = ['job']

@admin.register(Help)
class HelpAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'file', 'photo', 'url', 'access_level']
    list_per_page = 100

@admin.register(VendorCustomerPriceList)
class VendorCustomerPriceListAdmin(admin.ModelAdmin):
    list_display = ['id', 'vendor', 'customer', 'price_list']
    list_per_page = 100

@admin.register(CustomerFollowerEmail)
class CustomerFollowerEmailAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'email']
    list_per_page = 100

@admin.register(JobFollowerEmail)
class JobFollowerEmailAdmin(admin.ModelAdmin):
    list_display = ['id', 'job', 'email']
    list_per_page = 100

@admin.register(TailIdent)
class TailIdentAdmin(admin.ModelAdmin):
    list_display = ['id', 'tail_number', 'ident']
    list_per_page = 100

@admin.register(RetainerServiceActivity)
class RetainerServiceActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'timestamp', 'retainer_service', 'job', 'project_manager']
    list_per_page = 100


@admin.register(CustomerTail)
class CustomerTailAdmin(admin.ModelAdmin):
    list_display = ['id', 'tail_number', 'aircraft_type_name', 'status', 'is_interior_level_1_service_due', 'is_interior_level_2_service_due', 'is_exterior_level_1_service_due', 'is_exterior_level_2_service_due', 'customer', 'is_active']
    list_per_page = 100
    search_fields = ['tail_number']


@admin.register(TailAircraftLookup)
class TailAircraftLookupAdmin(admin.ModelAdmin):
    list_display = ['id', 'tail_number', 'aircraft_type', 'customer']
    list_per_page = 100
    search_fields = ['tail_number']



