from multiprocessing import parent_process
from django.shortcuts import render
from django.db import transaction
from rest_framework import viewsets, mixins, exceptions

from apps.endpoints import models
from apps.endpoints import serializers

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
                instance = serializers.save(active=True)
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