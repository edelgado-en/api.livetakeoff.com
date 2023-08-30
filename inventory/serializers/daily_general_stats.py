from rest_framework import serializers

from inventory.models import DailyGeneralStats

class DailyGeneralStatsSerializer(serializers.ModelSerializer):

    class Meta:
        model = DailyGeneralStats
        fields = ('id',
                'date',
                'total_items',
                'total_quantity',
                'total_cost',
                'total_moving_items',
                'total_moving_quantity',
                'total_moving_cost',
                'total_additions',
                'total_add_cost',
                'total_subtractions',
                'total_expense'
                )