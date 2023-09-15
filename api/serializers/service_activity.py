from rest_framework import serializers
from api.models import ServiceActivity

class ServiceActivitySerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    timestamp = serializers.DateTimeField(format="%m/%d/%Y", input_formats=['%m/%d/%Y'])
    purchase_order = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()
    tail_number = serializers.SerializerMethodField()
    airport_name = serializers.SerializerMethodField()
    fbo_name = serializers.SerializerMethodField()

    def get_service_name(self, obj):
        return obj.service.name
    
    def get_tail_number(self, obj):
        return obj.job.tailNumber

    def get_airport_name(self, obj):
        return obj.job.airport.name

    def get_fbo_name(self, obj):
        return obj.job.fbo.name
    
    def get_purchase_order(self, obj):
        return obj.job.purchase_order

    class Meta:
        model = ServiceActivity
        fields = ['id', 'timestamp' , 'purchase_order', 'service_name', 'price', 'tail_number', 'airport_name', 'fbo_name']