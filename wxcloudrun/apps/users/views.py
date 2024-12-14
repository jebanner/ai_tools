from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate
from wxcloudrun.apps.core.authentication.jwt_auth import JWTAuthentication
from wxcloudrun.apps.core.utils.response import success_response, error_response
from .models import User, AIUsageStats
from .serializers import (
    UserSerializer, 
    UserRegisterSerializer,
    UserLoginSerializer,
    AIUsageStatsSerializer
)

class UserViewSet(viewsets.ModelViewSet):
    """用户视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        if self.action in ['create', 'login', 'refresh_token']:
            return []
        return super().get_permissions()
        
    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        if self.action == 'login':
            return UserLoginSerializer
        return UserSerializer
        
    @action(detail=False, methods=['post'])
    def login(self, request):
        """用户登录"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        
        if not user:
            return error_response('用户名或密码错误', code=400)
            
        # 生成token
        token = JWTAuthentication.generate_token(user)
        
        return success_response({
            'token': token,
            'user': UserSerializer(user).data
        })
        
    @action(detail=False, methods=['post'])
    def refresh_token(self, request):
        """刷新token"""
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return error_response('请提供刷新令牌', code=400)
            
        try:
            new_token = JWTAuthentication.refresh_token(refresh_token)
            return success_response({'token': new_token})
        except Exception as e:
            return error_response(str(e), code=400)
            
    @action(detail=False)
    def profile(self, request):
        """获取个人信息"""
        serializer = UserSerializer(request.user)
        return success_response(serializer.data)
        
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """更新个人信息"""
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(serializer.data)
        
    @action(detail=False, methods=['post'])
    def wx_login(self, request):
        """微信小程序登录"""
        code = request.data.get('code')
        if not code:
            return error_response('请提供code', code=400)
            
        try:
            # 调用微信接口获取openid
            openid = self._get_wx_openid(code)
            
            # 查找或创建用户
            user, created = User.objects.get_or_create(
                openid=openid,
                defaults={
                    'username': f'wx_{openid[:8]}',  # 生成临时用户名
                    'nickname': request.data.get('nickname', ''),
                    'avatar': request.data.get('avatar', '')
                }
            )
            
            # 生成token
            token = JWTAuthentication.generate_token(user)
            
            return success_response({
                'token': token,
                'user': UserSerializer(user).data,
                'is_new': created
            })
        except Exception as e:
            return error_response(str(e), code=400)
            
    def _get_wx_openid(self, code):
        """获取微信openid"""
        from django.conf import settings
        import requests
        
        url = 'https://api.weixin.qq.com/sns/jscode2session'
        params = {
            'appid': settings.WX_APPID,
            'secret': settings.WX_SECRET,
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        
        response = requests.get(url, params=params)
        result = response.json()
        
        if 'errcode' in result:
            raise Exception(result.get('errmsg', '获取openid失败'))
            
        return result['openid']

class AIUsageStatsViewSet(viewsets.ModelViewSet):
    """AI调用统计视图集"""
    serializer_class = AIUsageStatsSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return AIUsageStats.objects.filter(user=self.request.user)
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user) 