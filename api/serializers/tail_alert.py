from rest_framework import serializers

from api.models import (TailAlert)

from api.serializers.tail_file import (TailFileSerializer)

class TailAlertSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    author = serializers.ReadOnlyField(source='author.username')
    files = TailFileSerializer(many=True)

    class Meta:
        model = TailAlert
        fields = (
            'id',
            'tailNumber',
            'message',
            'notes',
            'author',
            'created_at',
            'updated_at',
            'files'
        )