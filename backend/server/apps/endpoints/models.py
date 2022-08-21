from django.db import models

# Create your models here.
class Endpoint(models.Model):
    '''
    The Endpoint object represents ML API endpoint

    Attributes:
        name: the name of the endpoint, it will be used in the API URL
        owner: a string with the owner name
        created_at: the date when endpoint was created
    '''
    name = models.CharField(max_length=128)
    owner = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

class MLAlgorithm(models.Model):
    '''
    The MLAlgorithm represents the ML algorithm object

    Attributes:
        name: the name of the algorithm
        description: the short description of how the algorithm works
        code: the code of the algorithm
        version: the version of the algorithm similar to software versioning
        owner: the name of the owner 
        created_at: the date when MLAlgorithm was added
        parent_endpoint: the reference to the Endpoint
    '''

    name = models.CharField(max_length=128)
    description = models.CharField(max_length=1000)
    code = models.CharField(max_length=50000)
    version = models.CharField(max_length=128)
    owner = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    parent_endpoint = models.ForeignKey(Endpoint, on_delete=models.CASCADE)

class MLAlgorithmStatus(models.Model):
    '''
    The MLAlgorithmStatus represents the status of the MLAlgorithm which can 
    change during the time.

    Attributes:
        status: the status of the algorithm in the endpoint (testing, staging, production, ab_testing).
        active: the boolean flag which point to currently active status
        created_by: the name of the creator
        created_at: the date of status creation
        parent_mlalgorithm: the reference to corresponding MLAlgorithm 
    '''

    status = models.CharField(max_length=128)
    active = models.BooleanField()
    created_by = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    parent_mlalgorithm = models.ForeignKey(MLAlgorithm, on_delete=models.CASCADE, related_name='status')

class MLRequest(models.Model):
    '''
    The MLRequest will keep information about all requests to ML algorithms.

    Attributes:
        input_data: the input data to ML algorithm in JSON format
        full_response: the response of the ML algorithm
        response: the response of the ML algorithm in JSON format
        feedback: the feedback about the response in JSON format
        created_at: the date when request was created
        parent_mlalgorithm: the reference to ML Algorithm used to compute response
    '''

    input_data = models.CharField(max_length=10000)
    full_response = models.CharField(max_length=10000)
    response = models.CharField(max_length=10000)
    feedback = models.CharField(max_length=10000, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    parent_mlalgorithm = models.ForeignKey(MLAlgorithm, on_delete=models.CASCADE)

class ABTest(models.Model):
    '''
    The ABTest will keep information about A/B tests.

    Attributes:
        title: the title of the test
        created_by: the name of the creator
        created_at: the date of test created
        ended_at: the date of test stop
        summary: the description with test summary, created at test stop
        parent_mlalgorithm_1: The reference to the first corresponding MLAlgorithm.
        parent_mlalgorithm_2: The reference to the second corresponding MLAlgorithm.
    '''

    title = models.CharField(max_length=10000)
    created_by = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    summary = models.CharField(max_length=10000, blank=True, null=True)
    
    parent_mlalgorithm_1 =models.ForeignKey(MLAlgorithm, on_delete=models.CASCADE, related_name="parent_mlalgorithm_1")
    parent_mlalgorithm_2 =models.ForeignKey(MLAlgorithm, on_delete=models.CASCADE, related_name="parent_mlalgorithm_2")