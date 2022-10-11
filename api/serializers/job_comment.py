from rest_framework import serializers
from ..models import JobComments
from .basic_user import BasicUserSerializer

class JobCommentSerializer(serializers.ModelSerializer):
    author = BasicUserSerializer(required=False)

    class Meta:
        model = JobComments
        fields = ('id', 'comment', 'author', 'created')