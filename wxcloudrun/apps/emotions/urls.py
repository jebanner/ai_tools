from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmotionRecordViewSet

router = DefaultRouter()
router.register(r'records', EmotionRecordViewSet, basename='emotion-record')

urlpatterns = [
    path('', include(router.urls)),
] 