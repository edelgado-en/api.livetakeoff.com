from rest_framework import serializers

from api.models import (TailAlert)

class TailAlertSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = TailAlert
        fields = (
            'id',
            'tailNumber',
            'message',
            'notes',
            'author',
            'created_at',
            'updated_at'
        )