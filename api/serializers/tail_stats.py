from rest_framework import serializers


class TailStatsSerializer(serializers.Serializer):
    tailNumber = serializers.CharField()
    aircraftType__name = serializers.CharField()
    job_count = serializers.IntegerField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
