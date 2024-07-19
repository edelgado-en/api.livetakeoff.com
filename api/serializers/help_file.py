from rest_framework import serializers

from ..models import Help

class HelpFileSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    created_at = serializers.DateTimeField(format="%m/%d/%y %H:%M", read_only=True)

    class Meta:
        model = Help
        fields = ['id', 'created_at', 'name', 'file_type', 'description',  'file', 'photo', 'url', 'access_level']