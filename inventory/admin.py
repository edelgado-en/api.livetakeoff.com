from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from inventory.models import (
    Brand,
    Item,
    ItemTag,
    Location,
    LocationItem,
    LocationItemActivity,
    LocationUser,
    Provider,
    Tag,
    ItemProvider
)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'active']
    list_per_page = 100
    ordering = ['name', 'active']
    search_fields = ['name', 'active']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'active']
    list_per_page = 100
    ordering = ['name', 'active']
    search_fields = ['name', 'active']


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'url', 'active']
    list_per_page = 100
    ordering = ['name', 'active']
    search_fields = ['name', 'active']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'color']
    list_per_page = 100
    ordering = ['name']
    search_fields = ['name']


@admin.register(ItemTag)
class ItemTagAdmin(admin.ModelAdmin):
    list_display = ['id', 'item', 'tag']
    list_per_page = 100
    ordering = ['item', 'tag']
    search_fields = ['item', 'tag']


@admin.register(ItemProvider)
class ItemProviderAdmin(admin.ModelAdmin):
    list_display = ['id', 'item', 'provider']
    list_per_page = 100
    ordering = ['item', 'provider']
    search_fields = ['item', 'provider']


@admin.register(LocationUser)
class LocationUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'location', 'user', 'is_default']
    list_per_page = 100
    ordering = ['location', 'user']
    search_fields = ['location', 'user']


@admin.register(LocationItem)
class LocationItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'location', 'item', 'quantity', 'minimum_required', 'status']
    list_per_page = 100
    ordering = ['location', 'item', 'quantity']
    search_fields = ['location', 'item']


@admin.register(LocationItemActivity)
class LocationItemActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'location_item', 'activity_type', 'quantity', 'price', 'moved_from', 'moved_to', 'user']
    list_per_page = 100
    ordering = ['location_item', 'activity_type']
    search_fields = ['location_item', 'activity_type']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'timestamp', 'name', 'description', 'brand', 'measure_by', 'area', 'cost_per_unit', 'photo', 'created_by', 'active']
    list_per_page = 100
    ordering = ['name', 'active']
    search_fields = ['name', 'active']