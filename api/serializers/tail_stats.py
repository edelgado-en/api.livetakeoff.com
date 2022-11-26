from rest_framework import serializers


class TailStatsSerializer(serializers.Serializer):
    tailNumber = serializers.CharField()
    aircraftType__name = serializers.CharField()
    job_count = serializers.IntegerField()
