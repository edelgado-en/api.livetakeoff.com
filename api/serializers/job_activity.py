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
        elif obj.job.accepted_full_name and obj.status == 'S' and obj.activity_type == 'V':
            return obj.job.accepted_full_name

        elif obj.job.returned_full_name and obj.status == 'A' and obj.activity_type == 'R':
            return obj.job.returned_full_name

        elif obj.activity_type == 'S' and obj.status == 'S' and obj.user is None:
            # This accounts for auto-assignment
            return 'Livetakeoff'
        else:
            if obj.user:
                return obj.user.first_name + ' ' + obj.user.last_name
            else:
                return 'None'

    class Meta:
        model = JobStatusActivity
        fields = (
            'id',
            'status',
            'price',
            'user',
            'timestamp',
            'activity_type',
            'user_full_name',
            'service_name'
            )