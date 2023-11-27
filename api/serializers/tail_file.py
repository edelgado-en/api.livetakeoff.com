from rest_framework import serializers

from api.models import TailFile

class TailFileSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    size = serializers.ReadOnlyField()
    created_at = serializers.DateTimeField(format="%m/%d/%y %H:%M", read_only=True)

    class Meta:
        model = TailFile
        fields = ['id', 'created_at', 'name', 'file', 'size', 'is_public']