from django.contrib import admin
from . import models

@admin.register(models.Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'active']
    list_per_page = 100
    ordering = ['name', 'active']
    search_fields = ['name', 'active']

    def has_delete_permission(self, request, obj=None):
        # Disable delete because when you want to stop using a service, just set it to inactive
        return False

@admin.register(models.RetainerService)
class RetainerServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'active']
    list_per_page = 100
    ordering = ['name', 'active']
    search_fields = ['name', 'active']

    def has_delete_permission(self, request, obj=None):
        # Disable delete because when you want to stop using a service, just set it to inactive
        return False

@admin.register(models.ChecklistAction)
class ChecklistActionAdmin(admin.ModelAdmin):
    list_display = ['name', 'active']
    list_per_page = 100
    ordering = ['name', 'active']
    search_fields = ['name', 'active']

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'billingAddress', 'emailAddress', 'billingInfo', 'active']
    list_per_page = 100
    ordering = ['name', 'emailAddress']
    search_fields = ['name', 'emailAddress']

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(models.AircraftType)
class AircraftTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'active']
    list_per_page = 100
    ordering = ['name', 'active']
    search_fields = ['name', 'active']

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(models.Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ['initials', 'name', 'active']
    list_per_page = 100
    ordering = ['initials', 'name', 'active']
    search_fields = ['initials', 'name', 'active']

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(models.FBO)
class FBOAdmin(admin.ModelAdmin):
    list_display = ['name', 'active']
    list_per_page = 100
    ordering = ['name', 'active']
    search_fields = ['name', 'active']

    def has_delete_permission(self, request, obj=None):
        return False

@admin.register(models.Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'requestDate', 'tailNumber', 'aircraftType', 'airport', 'fbo', 'estimatedETA', 'estimatedETD', 'completeBy', 'status']
    list_per_page = 100
    ordering = ['customer', 'aircraftType', 'tailNumber', 'airport', 'fbo', 'status']
    search_fields = ['customer', 'tailNumber', ]

    def has_delete_permission(self, request, obj=None):
        return False
