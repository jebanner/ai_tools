from django.urls import path
from .views import UserViewSet

urlpatterns = [
    path('register', UserViewSet.as_view({'post': 'register'}), name='user-register'),
    path('login', UserViewSet.as_view({'post': 'login'}), name='user-login'),
    path('info', UserViewSet.as_view({'get': 'retrieve', 'put': 'update'}), name='user-info'),
] 