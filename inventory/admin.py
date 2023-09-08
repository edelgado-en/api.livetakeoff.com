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
    ItemProvider,
    Group,
    LocationGroup,
    LocationItemBrand,
    DailyGeneralStats,
    DailyLocationStats,
    DailyStatsAudit
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
    list_display = ['id', 'location', 'item', 'quantity',  'minimum_required', 'threshold', 'status', 'on_hold']
    list_per_page = 100
    ordering = ['location', 'item', 'quantity']
    search_fields = ['location', 'item']


@admin.register(LocationItemActivity)
class LocationItemActivityAdmin(admin.ModelAdmin):
    list_display = ['id', 'timestamp', 'location_item', 'activity_type', 'quantity', 'cost', 'moved_from', 'moved_to', 'user']
    list_per_page = 100
    ordering = ['timestamp', 'activity_type']
    search_fields = ['location_item__item__name']


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'timestamp', 'name', 'description', 'measure_by', 'area', 'cost_per_unit', 'photo', 'created_by', 'active']
    list_per_page = 100
    ordering = ['name', 'active']
    search_fields = ['name', 'active']


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'description', 'active']
    list_per_page = 100
    ordering = ['name', 'active']
    search_fields = ['name', 'active']


@admin.register(LocationGroup)
class LocationGroupAdmin(admin.ModelAdmin):
    list_display = ['id', 'location', 'group']
    list_per_page = 100
    ordering = ['location', 'group']
    search_fields = ['location', 'group']


@admin.register(LocationItemBrand)
class LocationItemBrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'location_item', 'brand']
    list_per_page = 100
    ordering = ['location_item', 'brand']
    search_fields = ['location_item', 'brand']


@admin.register(DailyGeneralStats)
class DailyGeneralStatsAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'total_items', 'total_quantity', 'total_cost',
                    'total_moving_items', 'total_moving_quantity', 'total_moving_cost', 'total_additions', 'total_add_cost', 'total_subtractions', 'total_expense']
    list_per_page = 100
    ordering = ['date']
    search_fields = ['date']


@admin.register(DailyLocationStats)
class DailyLocationStatsAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'location', 'total_items', 'total_quantity', 'total_cost',
                    'total_moving_items', 'total_moving_quantity', 'total_moving_cost', 'total_additions', 'total_add_cost', 'total_subtractions', 'total_expense']
    list_per_page = 100
    ordering = ['date']
    search_fields = ['date']


@admin.register(DailyStatsAudit)
class DailyStatsAuditAdmin(admin.ModelAdmin):
    list_display = ['id', 'last_updated']