from rest_framework import serializers
from ..models import JobComments
from .basic_user import BasicUserSerializer

class JobCommentSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    author = BasicUserSerializer(required=False)
    created = serializers.ReadOnlyField()

    class Meta:
        model = JobComments
        fields = ('id', 'comment', 'author', 'created')