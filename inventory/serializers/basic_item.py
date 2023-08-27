from rest_framework import serializers
from django.db.models import Sum
from inventory.models import Item

class BasicItemSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    total_quantity = serializers.SerializerMethodField()
    total_locations_found = serializers.SerializerMethodField()

    #total_locations_found is calculated by the number of locations where the item has a quantity greater than 0 in LocationItems
    def get_total_locations_found(self, obj):
        total_locations_found = obj.location_items.filter(quantity__gt=0).count()
        return total_locations_found


    def get_total_quantity(self, obj):
        total_quantity = obj.location_items.aggregate(total_quantity=Sum('quantity'))
        return total_quantity['total_quantity']


    class Meta:
        model = Item
        fields = ('id', 'name', 'description', 'area', 'measure_by', 'cost_per_unit', 'photo', 'total_quantity', 'total_locations_found')