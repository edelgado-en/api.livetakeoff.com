from rest_framework import serializers
from ..models import FBO

class FBOSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = FBO
        fields = ('id', 'name', 'hours_of_operation', 'fee', 'fee_percentage')