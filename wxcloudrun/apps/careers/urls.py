from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CareerRecordViewSet

router = DefaultRouter()
router.register(r'records', CareerRecordViewSet, basename='career-record')

urlpatterns = [
    path('', include(router.urls)),
] 