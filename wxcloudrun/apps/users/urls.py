from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, AIUsageStatsViewSet

router = DefaultRouter()
router.register('users', UserViewSet)
router.register('ai-stats', AIUsageStatsViewSet, basename='ai-stats')

urlpatterns = [
    path('', include(router.urls)),
] 