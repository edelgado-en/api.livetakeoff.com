from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User
from datetime import datetime

from ..models import (
        CustomerRetainerService,
        RetainerService,
        Service,
        CustomerService,
    )

class CustomerRetainersServicesView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, id):
        # id represents the customer id. Get all the retainer services for this customer from CustomerRetainerService. if none is found, return all retainer services
        customer_retainer_services = CustomerRetainerService.objects.filter(customer=id).all()

        if not customer_retainer_services:
            retainer_services = RetainerService.objects.filter(is_special=False).order_by('name')
        
        else:
            retainer_service_ids = []
            for customer_retainer_service in customer_retainer_services:
                retainer_service_ids.append(customer_retainer_service.retainer_service.id)
            
            retainer_services = RetainerService.objects.filter(Q(id__in=retainer_service_ids)).all().order_by('name')

        customer_services = CustomerService.objects.filter(customer=id).all()

        if not customer_services:
            services = Service.objects.filter(is_special=False).order_by('name')

        else:
            service_ids = []
            for customer_service in customer_services:
                service_ids.append(customer_service.service.id)
            
            services = Service.objects.filter(Q(id__in=service_ids)).all().order_by('name')


        service_dtos = []
        for service in services:
            s = {
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'category': service.category
            }

            checklist_actions = service.checklistActions.all()
            checklist_action_dtos = []

            for checklist_action in checklist_actions:
                c = {
                    'id': checklist_action.id,
                    'name': checklist_action.name
                }

                checklist_action_dtos.append(c)

            s['checklist_actions'] = checklist_action_dtos

            service_dtos.append(s)

        retainer_service_dtos = []
        for retainer_service in retainer_services:
            r = {
                'id': retainer_service.id,
                'name': retainer_service.name,
                'description': retainer_service.description,
                'category': retainer_service.category
            }

            checklist_actions = retainer_service.checklistActions.all()
            checklist_action_dtos = []

            for checklist_action in checklist_actions:
                c = {
                    'id': checklist_action.id,
                    'name': checklist_action.name
                }

                checklist_action_dtos.append(c)

            r['checklist_actions'] = checklist_action_dtos

            retainer_service_dtos.append(r)

        
        return Response({'retainer_services': retainer_service_dtos, 'services': service_dtos}, status=status.HTTP_200_OK)