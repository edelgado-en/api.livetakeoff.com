from rest_framework import serializers

from ..models import VendorFile

class VendorFileSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    name = serializers.ReadOnlyField()
    size = serializers.ReadOnlyField()
    created_at = serializers.DateTimeField(format="%m/%d/%y %H:%M", read_only=True)

    class Meta:
        model = VendorFile
        fields = ['id', 'created_at', 'name', 'file', 'size']