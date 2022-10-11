from rest_framework import serializers
from ..models import JobComments
from .basic_user import BasicUserSerializer

class JobCommentSerializer(serializers.ModelSerializer):
    user = BasicUserSerializer()

    class Meta:
        model = JobComments
        fields = ('id', 'comment', 'user', 'created')