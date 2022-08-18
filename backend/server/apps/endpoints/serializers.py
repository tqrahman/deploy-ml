# Imports

from rest_framework import serializers
from apps.endpoints.models import Endpoint, MLAlgorithm, MLAlgorithmStatus, MLRequest

'''
serializers: define how database objects are mapped in requests
* helps with packing and unpacking database objects into JSON objects
'''

class EndpointSerializer(serializers.ModelSerializer):
    class Meta:
        '''
        Defining all fields read-only
            The fields will be created and modified in the server side
        '''
        model = Endpoint
        read_only_fields = ("id", "name", "owner", "created_at")
        fields = read_only_fields

class MLAlgorithmSerializer(serializers.ModelSerializer):

    current_status = serializers.SerializerMethodField(read_only=True)

    def get_current_status(self, mlalgorithm):
        return MLAlgorithmStatus.objects.filter(parent_mlalgorithm=mlalgorithm).latest('created_at').status
    
    class Meta:
        '''
        Defining all fields read-only
            The fields will be created and modified in the server side
        '''
        model = MLAlgorithm
        read_only_fields = (
            "id", "name", "description", "code",
            "version", "owner", "created_at",
            "parent_endpoint", "current_status"
        )
        fields = read_only_fields

class MLAlgorithmStatusSerializer(serializers.ModelSerializer):
    class Meta:
        '''
        The fields: status, created_by, created_at and parent_mlalgorithm are in read and write mode
        It will be modified using the REST API
        '''
        model = MLAlgorithmStatus
        read_only_fields = ("id", "active")
        fields = (
            "id", "active", "status", "created_by", "created_at",
            "parent_mlalgorithm"
        )

class MLRequestSerializer(serializers.ModelSerializer):
    class Meta:
        '''
        feedback field that is left in read and write mode - it will be needed to provide feedback about predictions to the server
        '''
        model = MLRequest
        read_only_fields = (
            "id",
            "input_data",
            "full_response",
            "response",
            "created_at",
            "parent_mlalgorithm",
        )

        fields =  (
            "id",
            "input_data",
            "full_response",
            "response",
            "feedback",
            "created_at",
            "parent_mlalgorithm",
        )