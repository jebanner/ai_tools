from django.urls import path, include
from . import views

urlpatterns = [
    path('api/count', views.counter),  # 计数器接口
    path('api/emotions/', include('wxcloudrun.apps.emotions.urls')),
    path('api/collections/', include('wxcloudrun.apps.collections.urls')),
    path('api/careers/', include('wxcloudrun.apps.careers.urls')),
    path('api/users/', include('wxcloudrun.apps.users.urls')),
]
