import csv
from django.http import HttpResponse
from rest_framework.views import APIView
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from api.models import (Job, PriceList, AircraftType, Service)


class PriceListExportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, format=None):
        if not self.can_export(request.user):
            return Response({'error': 'You do not have permission to export jobs'}, status=status.HTTP_403_FORBIDDEN)
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="export.csv"'

        field_names = ['Aircraft Type', 'Service']

        price_lists = PriceList.objects.all().order_by('id')
        for price_list in price_lists:
            field_names.append(price_list.name)

        writer = csv.DictWriter(response, fieldnames=field_names)
        writer.writeheader()

        aircraft_types = AircraftType.objects.all().order_by('name')
        services = Service.objects.all().order_by('name')

        for aircraft_type in aircraft_types:

            for service in services:
                row = {
                    'Aircraft Type': aircraft_type.name,
                    'Service': service.name
                }

                for price_list in price_lists:
                    price = price_list.entries.filter(aircraft_type=aircraft_type, service=service).first()
                    row[price_list.name] = price.price if price else ''

                writer.writerow(row)

        return response


    def can_export(self, user):
        return user.is_superuser \
                or user.is_staff \
                or user.groups.filter(name='Account Managers').exists() \
                or user.groups.filter(name='Internal Coordinators').exists()