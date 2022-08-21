# backend/server/apps/endpoints/urls.py file

from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter

from apps.endpoints.views import EndpointViewSet
from apps.endpoints.views import MLAlgorithmViewSet
from apps.endpoints.views import MLAlgorithmStatusViewSet
from apps.endpoints.views import MLRequestViewSet
from apps.endpoints.views import ABTestViewSet, StopABTestView
from .views import PredictView

router = DefaultRouter(trailing_slash=False)
router.register(r"endpoints", EndpointViewSet, basename="endpoints")
router.register(r"mlalgorithms", MLAlgorithmViewSet, basename="mlalgorithms")
router.register(r"mlalgorithmstatuses", MLAlgorithmStatusViewSet, basename="mlalgorithmstatuses")
router.register(r"mlrequests", MLRequestViewSet, basename="mlrequests")
router.register(r"abtests", ABTestViewSet, basename="abtests")

urlpatterns = [
    path("api/v1/", include(router.urls)),
    re_path(r"^api/v1/(?P<endpoint_name>.+)/predict$", PredictView.as_view(), name="predict"),
    re_path(r"^api/v1/stop_ab_test/(?P<ab_test_id>.+)", StopABTestView.as_view(), name="stop_ab"),
]

'''
Creates REST API routers to database models. 
The models will be accessed by following the URL pattern:

http://<server-ip>/api/v1/<object-name> 
'''