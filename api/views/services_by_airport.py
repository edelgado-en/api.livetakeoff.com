from django.db.models import Q, F
from django.db import models
from django.db.models import Count, Sum, Func
from django.shortcuts import get_object_or_404
from rest_framework import (permissions, status)
from rest_framework .response import Response
from rest_framework.views import APIView

from api.models import (
    JobServiceAssignment,
    JobRetainerServiceAssignment,
    Airport,
    Job
)



class ServiceByAirportView(APIView):
    permission_classes = (permissions.IsAuthenticated,)


    def get(self, request):

        accepted_data = self.getAirportDataByAcceptedJobs()
        assigned_data = self.getAirportDataByStatus('A')
        wip_data = self.getAirportDataByStatus('W')

        data = {
            'accepted': accepted_data,
            'assigned': assigned_data,
            'wip': wip_data
        }


        return Response(data, status=status.HTTP_200_OK)


    def getAirportDataByAcceptedJobs(self):
        # only get airports where the job is accepted
        airports = Airport.objects.filter(job__status='A').distinct()
        
        services = JobServiceAssignment.objects.filter(
            job__airport__in=airports, status='U', job__status='A'
        ).values(
            'service__name',
            'job__airport__name'
        ).annotate(
            count=Count('service__name')
        ).order_by(
            '-count'
        )

        retainer_services = JobRetainerServiceAssignment.objects.filter(
            job__airport__in=airports, status='U', job__status='A'
        ).values(
            service__name=F('retainer_service__name'),
            job__airport__name=F('job__airport__name')
        ).annotate(
            count=Count('retainer_service__name')
        ).order_by(
            '-count'
        )

        services = list(services) + list(retainer_services)

        data = []
        for airport in airports:
            airport_data = {
                'name': airport.name,
                'services': []
            }

            for service in services:
                if service['job__airport__name'] == airport.name:
                    # only add service_data to airport_data if it doesn't already exist 
                    # this is to prevent duplicate services
                    if not any(d['name'] == service['service__name'] for d in airport_data['services']):
                        service_data = {
                            'name': service['service__name'],
                            'count': service['count']
                        }

                        airport_data['services'].append(service_data)
            
            data.append(airport_data)


        return data



    def getAirportDataByStatus(self, status):
        # get a list of airports that have job service assignments with status assigned (S). A job service assignment has a job, and a job has an airport
        # this is the list of airports that have jobs with services assigned to them
        airports = Airport.objects.filter(job__job_service_assignments__status=status).distinct()


        # get a list of all the services that are currently assigned to an airport
        # add filter to only include status = assigned (A)
        services = JobServiceAssignment.objects.filter(
            job__airport__in=airports, status=status
        ).values(
            'service__name',
            'job__airport__name'
        ).annotate(
            count=Count('service__name')
        ).order_by(
            '-count'
        )

        # get a list of all the retainer services that are currently assigned to an airport
        retainer_services = JobRetainerServiceAssignment.objects.filter(
            job__airport__in=airports, status=status
        ).values(
            service__name=F('retainer_service__name'),
            job__airport__name=F('job__airport__name')
        ).annotate(
            count=Count('retainer_service__name')
        ).order_by(
            '-count'
        )

        # merge services and retainer_services into one list
        services = list(services) + list(retainer_services)

        # get a list of all the users that are currently assigned to a service
        users = JobServiceAssignment.objects.filter(
            job__airport__in=airports, status=status
        ).values(
            'service__name',
            'job__airport__name',
            'project_manager__profile__avatar',
            'project_manager__username',
            'project_manager__first_name',
            'project_manager__last_name'
        ).annotate(
            count=Count('project_manager__username')
        ).order_by(
            '-count'
        )

        # get a list of all the users that are currently assigned to a retainer service
        retainer_users = JobRetainerServiceAssignment.objects.filter(
            job__airport__in=airports, status=status
        ).values(
            service__name=F('retainer_service__name'),
            job__airport__name=F('job__airport__name'),
            project_manager__profile__avatar=F('project_manager__profile__avatar'),
            project_manager__username=F('project_manager__username'),
            project_manager__first_name=F('project_manager__first_name'),
            project_manager__last_name=F('project_manager__last_name')
        ).annotate(
            count=Count('project_manager__username')
        ).order_by(
            '-count'
        )

        # combine the two lists of users
        users = list(users) + list(retainer_users)

        # create a list of dictionaries
        # each dictionary is an airport
        # each airport has a list of services
        # each service has a list of users
        # each user has a count of how many times they are assigned to that service
        data = []
        for airport in airports:
            airport_data = {
                'name': airport.name,
                'services': []
            }

            for service in services:
                if service['job__airport__name'] == airport.name:
                    # only add service_data to airport_data if it doesn't already exist 
                    # this is to prevent duplicate services
                    if not any(d['name'] == service['service__name'] for d in airport_data['services']):
                        service_data = {
                            'name': service['service__name'],
                            'count': service['count'],
                            'users': []
                        }

                        for user in users:
                            if user['job__airport__name'] == airport.name and user['service__name'] == service['service__name']:
                                # if user_data already exists in service_data['users'] then add the count to the existing user_data
                                # otherwise create a new user_data
                                if any(d['username'] == user['project_manager__username'] for d in service_data['users']):
                                    for user_data in service_data['users']:
                                        if user_data['username'] == user['project_manager__username']:
                                            user_data['count'] += user['count']
                                else:
                                    user_data = {
                                        'avatar': user['project_manager__profile__avatar'],
                                        'username': user['project_manager__username'],
                                        'first_name': user['project_manager__first_name'],
                                        'last_name': user['project_manager__last_name'],
                                        'count': user['count']
                                    }
                                    service_data['users'].append(user_data)
                                

                        airport_data['services'].append(service_data)
            
            data.append(airport_data)


        return data
    
