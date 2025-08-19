from django.db.models import Q
from django.shortcuts import get_object_or_404
from io import BytesIO
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django_q.tasks import async_task
from django.db import transaction
from django.http import FileResponse, Http404

from api.serializers.export_job import ExportJobSerializer

from api.models import (
        ExportJob
    )

class ExportJobDetailView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = ExportJobSerializer

    def post(self, request):
        customer = None
        if request.user.profile.customer: 
            customer = request.user.profile.customer

        with transaction.atomic():
            ej = ExportJob.objects.create(
                user=request.user,
                params=request.data or {},
                customer=customer
            )

            # Enqueue ONLY AFTER the row is committed
            transaction.on_commit(lambda: async_task("api.tasks.run_export", ej.id))

        return Response(ExportJobSerializer(ej).data, status=status.HTTP_201_CREATED)

    def get(self, request, id):
        try:
            ej = ExportJob.objects.get(id=id)
        except ExportJob.DoesNotExist:
            raise Http404

        if not ej.file_bytes:
            raise Http404  # or return 409 if job not ready

        buf = BytesIO(ej.file_bytes)  # or open(ej.file.path, 'rb') if FileField
        filename = ej.filename or 'export.zip'
        response = FileResponse(buf, as_attachment=True, filename=filename)
        
        # Optional: set a more precise content type
        response['Content-Type'] = 'application/zip'

        return response
