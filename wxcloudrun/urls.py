from django.urls import path, include
from django.http import HttpResponse
from . import views

def health_check(request):
    """健康检查端点"""
    return HttpResponse("ok")

urlpatterns = [
    # 健康检查路由
    path('health/', health_check, name='health_check'),
    
    # API v1 路由
    path('api/v1/', include([
        path('emotions/', include('wxcloudrun.apps.emotions.urls')),
        path('collections/', include('wxcloudrun.apps.collections.urls')),
        path('careers/', include('wxcloudrun.apps.careers.urls')),
        path('user/', include('wxcloudrun.apps.users.urls')),
    ])),
]
