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
    UserProfile,
    CustomerProjectManager,
    CustomerDiscount,
    CustomerDiscountService,
    CustomerDiscountAirport,
    CustomerAdditionalFee,
    CustomerAdditionalFeeAirport,
    CustomerAdditionalFeeFBO,
    CustomerRetainerService,
    PriceList,
    PriceListEntries,
    EstimatedServiceTime,
    JobStatusActivity,
    JobServiceAssignment,
    JobRetainerServiceAssignment,
    Tag,
    JobEstimate,
    JobServiceEstimate
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
    list_display = ['id', 'name', 'description', 'active', 'public', 'type', 'category']
    list_per_page = 100
    ordering = ['name', 'active']
    search_fields = ['name', 'active']

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
    list_display = ['name', 'description', 'active', 'category']
    list_per_page = 100
    ordering = ['name', 'active']
    search_fields = ['name', 'active']

    def has_delete_permission(self, request, obj=None):
        # Disable delete because when you want to stop using a service, just set it to inactive
        return False

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
    list_display = ['id', 'name', 'logo', 'banner', 'about', 'contact',  'phone_number', 'billingAddress', 'emailAddress', 'billingInfo', 'active']
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
    list_display = ['id', 'customer', 'show_spending_info', 'allow_cancel_job', 'retainer_amount', 'special_instructions', 'price_list']
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
    list_display = ['customer_setting', 'retainer_service', 'count']


@admin.register(PriceList)
class PriceListAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description']


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
    list_display = ['initials', 'name', 'active', 'public']
    list_per_page = 100
    ordering = ['initials', 'name', 'active']
    search_fields = ['initials', 'name', 'active']

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(FBO)
class FBOAdmin(admin.ModelAdmin):
    list_display = ['name', 'active', 'public']
    list_per_page = 100 
    ordering = ['name', 'active']
    search_fields = ['name', 'active']

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['id', 'created_at', 'purchase_order', 'customer', 'requestDate', 'tailNumber', 'aircraftType', 'airport', 'fbo', 'estimatedETA', 'estimatedETD', 'completeBy', 'status', 'estimated_completion_time', 'actual_completion_time', 'price']
    list_per_page = 100
    ordering = ['created_at', 'purchase_order', 'customer', 'aircraftType', 'tailNumber', 'airport', 'fbo', 'status', 'completeBy']
    search_fields = ['purchase_order', 'customer', 'tailNumber', ]

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(JobStatusActivity)
class JobStatusActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'timestamp', 'status', 'job', 'user']
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
    list_display = ['id', 'name', 'active']
    list_per_page = 100
    search_fields = ['name']


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


