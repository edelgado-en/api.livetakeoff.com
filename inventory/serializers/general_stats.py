from rest_framework import serializers

class GeneralStatsSerializer(serializers.Serializer):

    date__month = serializers.IntegerField(required=False)
    date__week = serializers.IntegerField(required=False)
    date_name = serializers.CharField(required=False)
    total_moving_items = serializers.IntegerField()
    total_moving_quantity = serializers.IntegerField()
    total_moving_cost = serializers.DecimalField(max_digits=9, decimal_places=2)
    total_additions = serializers.IntegerField()
    total_add_cost = serializers.DecimalField(max_digits=9, decimal_places=2)
    total_subtractions = serializers.IntegerField()
    total_expense = serializers.DecimalField(max_digits=9, decimal_places=2)
