from django.db.models import Q, F
from rest_framework import (permissions,status)
from rest_framework .response import Response
from rest_framework.generics import ListAPIView
from ..serializers import (
        JobScheduleSerializer,
    )

from pathlib import Path
import json

from django.contrib.auth.models import User

from ..pagination import CustomPageNumberPagination
from ..models import (
        JobSchedule,
        UserProfile
    )

class JobScheduleListView(ListAPIView):
    serializer_class = JobScheduleSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        tailNumber = self.request.data.get('tailNumber', None)

        qs = JobSchedule.objects.filter(is_deleted=False).order_by('-created_at')

        if tailNumber:
            qs = qs.filter(tailNumber__icontains=tailNumber)

        return qs


    def post(self, request, *args, **kwargs):

        json_path = Path(__file__).resolve().parent / "users.json"
        if not json_path.exists():
            raise FileNotFoundError(str(json_path))

        with open(json_path, "r") as f:
            payload = json.load(f)

        users = payload.get("users", [])

        # iterate over users and search User by username = user['email']
        for user in users:
            try:
                u = User.objects.get(username=user['email'])
                profile = UserProfile.objects.get(user=u)
                profile.is_job_submitter_only = True
                profile.save()
            except User.DoesNotExist:
                print(f"User {user['email']} does not exist")
            except UserProfile.DoesNotExist:
                print(f"UserProfile for {user['email']} does not exist")

        return self.list(request, *args, **kwargs)