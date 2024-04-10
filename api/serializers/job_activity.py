from rest_framework import serializers
from .basic_user import BasicUserSerializer
from api.models import JobStatusActivity


class JobActivitySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    user = BasicUserSerializer()

    user_full_name = serializers.SerializerMethodField()

    def get_user_full_name(self, obj):
        # get the obj.job.confirmed_full_name if it is not empty and the obj.status == 'A' and the obj.activity_type == 'S'
        if obj.job.confirmed_full_name and obj.status == 'A' and obj.activity_type == 'S':
            return obj.job.confirmed_full_name
        else:
            # return the obj.user.first_name + ' ' + obj.user.last_name
            return obj.user.first_name + ' ' + obj.user.last_name

    class Meta:
        model = JobStatusActivity
        fields = (
            'id',
            'status',
            'price',
            'user',
            'timestamp',
            'activity_type',
            'user_full_name'
            )