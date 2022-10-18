from rest_framework import serializers
from django.contrib.auth.models import User
from ..models import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()

    class Meta:
        model = UserProfile
        fields = ('id', 'avatar')


class BasicUserSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    first_name = serializers.ReadOnlyField()
    last_name = serializers.ReadOnlyField()
    profile = UserProfileSerializer()
    availability = serializers.CharField(allow_null=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'profile', 'availability')


