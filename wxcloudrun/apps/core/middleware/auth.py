import jwt
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from wxcloudrun.apps.users.models import User

class AuthMiddleware(MiddlewareMixin):
    """认证中间件"""

    def process_request(self, request):
        # 白名单路径不需要认证
        white_list = [
            '/api/v1/users/login/',
            '/api/v1/users/register/',
            '/api/v1/users/refresh-token/',
            '/admin/',
        ]
        
        if request.path in white_list or request.path.startswith('/admin/'):
            return None
            
        # 获取认证头
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return JsonResponse({
                'code': 401,
                'message': '未提供认证信息'
            }, status=401)
            
        try:
            # 解析token
            token_type, token = auth_header.split(' ')
            if token_type.lower() != 'bearer':
                raise ValueError('无效的认证类型')
                
            # 验证token
            payload = jwt.decode(
                token,
                settings.JWT_SETTINGS['SECRET_KEY'],
                algorithms=[settings.JWT_SETTINGS['ALGORITHM']]
            )
            
            # 获取用户
            user = User.objects.get(id=payload['user_id'])
            request.user = user
            
        except (ValueError, jwt.InvalidTokenError, User.DoesNotExist) as e:
            return JsonResponse({
                'code': 401,
                'message': '无效的认证信息'
            }, status=401)
            
        return None 