from rest_framework import serializers
from .aircraft_type import AircraftTypeSerializer
from .airport import AirportSerializer
from .fbo import FBOSerializer
from .customer import CustomerSerializer
from ..models import Job

class JobCompletedSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    customer = CustomerSerializer()
    aircraftType = AircraftTypeSerializer()
    airport = AirportSerializer()
    fbo = FBOSerializer()
    completeBy = serializers.DateTimeField(format="%m/%d/%y %H:%M")
    estimatedETA = serializers.DateTimeField(format="%m/%d/%y %H:%M")
    estimatedETD = serializers.DateTimeField(format="%m/%d/%y %H:%M")
    requestDate = serializers.DateTimeField(format="%m/%d/%y %H:%M", read_only=True)
    completion_date = serializers.DateTimeField(format="%m/%d/%y %H:%M", read_only=True)

    labor_time = serializers.SerializerMethodField()

    # def get_labor_time(self, obj):
    # to calculate labor time do the following:
    # get the hours_worked and minutes_worked
    # convert the hours_worked to minutes and add them to minutes_worked
    # now convert it to hours and multiply by the number of workers. The result should be in decimal format (e.g. 1.5)
    # return the result

    def get_labor_time(self, obj):
        hours_worked = obj.hours_worked
        minutes_worked = obj.minutes_worked
        number_of_workers = obj.number_of_workers

        if hours_worked is None:
            hours_worked = 0

        if minutes_worked is None:
            minutes_worked = 0
        
        if number_of_workers is None:
            number_of_workers = 0

        total_minutes = (hours_worked * 60) + minutes_worked
        total_hours = total_minutes / 60
        total_labor_time = total_hours * number_of_workers
        
        # total_labor_time should be rounded to only one decimal place
        total_labor_time = round(total_labor_time, 1)

        return total_labor_time

    class Meta:
        model = Job
        fields = (
            'id',
            'tailNumber',
            'requestDate',
            'estimatedETA',
            'estimatedETD',
            'completeBy',
            'status',
            'customer',
            'purchase_order',
            'customer_purchase_order',
            'aircraftType',
            'airport',
            'fbo',
            'completeBy',
            'price',
            'is_auto_priced',
            'on_site',
            'completion_date',
            'labor_time'
            )
