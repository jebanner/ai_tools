"""wxcloudrun URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from wxcloudrun import views

urlpatterns = [
    # 计数器接口
    path('api/count', views.counter, name='counter'),
    # 获取主页
    path('', views.index),
    # 用户相关接口
    path('api/user/register', views.user_register, name='user_register'),
    path('api/user/login', views.user_login, name='user_login'),
    path('api/user/info', views.user_info, name='user_info'),
]
