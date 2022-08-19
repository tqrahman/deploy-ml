'''
This ML Registry app keeps information about available algorithms 
and corresponding endpoints.

Keeps simple dictionary object that maps algorithm id to algorithm object
'''

# Imports
from apps.endpoints.models import Endpoint, MLAlgorithm, MLAlgorithmStatus

class MLRegistry:

    def __init__(self):
        self.endpoints = {}
    
    def add_algorithm(
        self, endpoint_name, algorithm_object, algorithm_name,
        algorithm_status, algorithm_version, owner, algorithm_description,
        algorithm_code
    ):
        
        # Get endpoint
        endpoint, _ = Endpoint.objects.get_or_create(name=endpoint_name, owner=owner)

        # Get algorithm
        database_object, algorithm_created = MLAlgorithm.objects.get_or_create(
            name=algorithm_name,
            description=algorithm_description,
            code=algorithm_code,
            version=algorithm_version,
            owner=owner,
            parent_endpoint=endpoint
        )
        if algorithm_created:
            status = MLAlgorithmStatus(
                status=algorithm_status,
                created_by=owner,
                parent_mlalgorithm=database_object,
                active=True
            )
            
            status.save()

        self.endpoints[database_object.id] = algorithm_object