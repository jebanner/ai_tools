from django.urls import path, include
from . import views

urlpatterns = [
    # API v1 路由
    path('api/v1/', include([
        path('emotions/', include('wxcloudrun.apps.emotions.urls')),
        path('collections/', include('wxcloudrun.apps.collections.urls')),
        path('careers/', include('wxcloudrun.apps.careers.urls')),
        path('user/', include('wxcloudrun.apps.users.urls')),
    ])),
]
