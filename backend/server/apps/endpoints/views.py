import json
from numpy.random import rand
import datetime

from django.shortcuts import render
from django.db import transaction
from django.db.models import F
from rest_framework import viewsets, mixins, exceptions, views, status
from rest_framework.response import Response

from multiprocessing import parent_process
# from .models import ABTest
# from .models import MLAlgorithm, MLRequest, ABTest

from server.wsgi import registry
from apps.endpoints import models
from apps.endpoints import serializers
from apps.ml.registry import MLRegistry

# Create your views here.
class EndpointViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    '''
    Create a view where user can retrieve an Endpoint object.
    '''
    serializer_class = serializers.EndpointSerializer
    queryset = models.Endpoint.objects.all()

class MLAlgorithmViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    '''
    Create a view where user can retrieve the MLAlgorithm used and view it
    '''

    serializer_class = serializers.MLAlgorithmSerializer
    queryset = models.MLAlgorithm.objects.all()

def deactivate_other_statuses(instance):
    old_statuses = models.MLAlgorithmStatus.objects.filter(
        parent_mlalgorithm = instance.parent_mlalgorithm,
        created_at__lt = instance.created_at,
        active=True
    )
    
    for i in range(len(old_statuses)):
        old_statuses[i].active = False
    models.MLAlgorithmStatus.objects.bulk_update(old_statuses, ['active'])

class MLAlgorithmStatusViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin,
    viewsets.GenericViewSet, mixins.CreateModelMixin
):
    serializer_class = serializers.MLAlgorithmStatusSerializer
    queryset = models.MLAlgorithmStatus.objects.all()
    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                instance = serializer.save(active=True)
                # set active=False for other statuses
                deactivate_other_statuses(instance)

        except Exception as e:
            raise exceptions.APIException(str(e))

class MLRequestViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet,
    mixins.UpdateModelMixin
):
    serializer_class = serializers.MLRequestSerializer
    queryset = models.MLRequest.objects.all()

class PredictView(views.APIView):
    '''
    Only accepts POST requests.
    Available at https://<server_ip/>api/v1/<endpoint_name>/predict

    Based on the endpoint name, status, and version, there is a routing 
    of the request to correct ML algorithm
    '''
    def post(self, request, endpoint_name, format=None):

        # Getting the status
        algorithm_status = self.request.query_params.get("status", "production")
        
        # Getting the version
        algorithm_version = self.request.query_params.get("version")

        # Getting the id
        algorithm_id = self.request.query_params.get("id")

        algs = models.MLAlgorithm.objects.filter(
            parent_endpoint__name=endpoint_name,
            status__status=algorithm_status,
            status__active=True 
        )

        # Get the algorithm that matches the version
        if algorithm_version is not None:
            algs = algs.filter(version=algorithm_version)
        
        # Check to see if there are algorithms
        if len(algs) == 0:
            return Response(
                {
                    "status":"Error",
                    "message":"ML algorithm is not available."
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # # Check to see if there are more than one algorithms
        # if len(algs) != 1 and algorithm_status != "ab_testing":
        #     return Response(
        #         {"status": "Error", "message": "ML algorithm selection is ambiguous. Please specify algorithm version."},
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )

        alg_index = 0

        if algorithm_status == "ab_testing":
            alg_index = 0 if rand() < 0.5 else 1

        # Extracting the algorithm
        algorithm_object = registry.endpoints[algs[alg_index].id]

        # Get the prediction of the given data
        prediction = algorithm_object.compute_prediction(request.data)

        # Extracting the label from prediction object
        label = prediction["label"] if "label" in prediction else "error"

        # Save the request to apply ML algorithm
        ml_request = models.MLRequest(
            input_data=json.dumps(request.data),
            full_response=prediction,
            response=label,
            feedback="",
            parent_mlalgorithm=algs[alg_index]
        )
        ml_request.save()

        prediction["request_id"] = ml_request.id

        return Response(prediction)

class ABTestViewSet(
    mixins.RetrieveModelMixin, mixins.ListModelMixin, mixins.GenericViewSet,
    mixins.CreateModelMixin, mixins.UpdateModelMixin
):
    # Unpacking request into JSON format
    serializer_class = serializers.ABTestSerializer
    
    # Getting all the ABTest objects
    queryset = models.ABTest.objects.all()

    def perform_create(self, serializer):
        '''
        Creates an ABTest object and two new statuses ("ab_testing") 
        for ML Algorithms
        '''
        try:
            with transaction.atomic():
                instance = serializer.save()

                # Update status for first algorithm
                status_1 = models.MLAlgorithmStatus(
                    status='ab_testing',
                    created_by=instance.created_by,
                    parent_mlalgorithm=instance.parent_mlalgorithm_1,
                    active=True
                )

                status_1.save()
                deactivate_other_statuses(status_1)
                
                # Update status for second algorithm
                status_2 = models.MLAlgorithmStatus(
                    status='ab_testing',
                    created_by=instance.created_by,
                    parent_mlalgorithm=instance.parent_mlalgorithm_2,
                    active=True
                )

                status_2.save()
                deactivate_other_statuses(status_2)
        
        except Exception as e:
            raise exceptions.APIException(str(e))

class StopABTestView(views.APIView):
    '''
    Stops the A/B test, computes the accuracy of the two algorithms, and 
    compares the two algorithms. The algorithm with the higher accuracy
    is set as production while the other algorithm is saved as testing 
    '''
    def post(self, request, ab_test_id, format=None):
        
        try:
            # Get the ABTest object that matches the id
            ab_test = models.ABTest.objects.get(pk=ab_test_id)

            if ab_test.ended_at is None:
                return Response({
                    "message":"AB Test already finished."
                })
            
            date_now = datetime.datetime.now()

            # Algorithm 1
            
            all_responses_1 = models.MLRequest.objects.filter(
                parent_algorithm=ab_test.parent_mlalgorithm_1,
                created_at__gt=ab_test.created_at,
                created_at__lt=date_now,
            ).count()

            correct_responses_1 = models.MLRequest.objects.filter(
                parent_algorithm=ab_test.parent_mlalgorithm_1,
                created_at__gt=ab_test.created_at,
                created_at__lt=date_now,
                response=F('feedback')
            ).count()

            accuracy_1 = correct_responses_1 / float(all_responses_1)

            print(all_responses_1, correct_responses_1, accuracy_1)

            # Algorithm 2

            all_responses_2 = models.MLRequest.objects.filter(
                parent_mlalgorithm=ab_test.parent_mlalgorithm_2, 
                created_at__gt = ab_test.created_at, 
                created_at__lt = date_now
            ).count()

            correct_responses_2 = models.MLRequest.objects.filter(
                parent_mlalgorithm=ab_test.parent_mlalgorithm_2, 
                created_at__gt = ab_test.created_at, 
                created_at__lt = date_now, 
                response=F('feedback')
            ).count()

            accuracy_2 = correct_responses_2 / float(all_responses_2)
            
            print(all_responses_2, correct_responses_2, accuracy_2)

            # Select the algorithm with higher accuracy
            
            alg_id_1, alg_id_2 = ab_test.parent_mlalgorithm_1, ab_test.parent_mlalgorithm_2
            
            # Swap
            if accuracy_1 < accuracy_2:
                alg_id_1, alg_id_2 = alg_id_2, alg_id_1
            
            # Update status of selected algorithm
            status_1 = models.MLAlgorithmStatus(status = "production",
                            created_by=ab_test.created_by,
                            parent_mlalgorithm = alg_id_1,
                            active=True)
            status_1.save()
            deactivate_other_statuses(status_1)
            
            # Update status for second algorithm
            status_2 = models.MLAlgorithmStatus(status = "testing",
                            created_by=ab_test.created_by,
                            parent_mlalgorithm = alg_id_2,
                            active=True)
            status_2.save()
            deactivate_other_statuses(status_2)

            summary = "Algorithm #1 accuracy: {}, Algorithm #2 accuracy: {}".format(accuracy_1, accuracy_2)
            ab_test.ended_at = date_now
            ab_test.summary = summary
            ab_test.save()

        except Exception as e:
            return Response(
                {
                    "status":"Error",
                    "message":str(e),
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "message":"AB Test finished.",
            "summary":summary
        })