import jwt
from datetime import datetime, timedelta
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions
from wxcloudrun.apps.users.models import User

class JWTAuthentication(authentication.BaseAuthentication):
    """JWT认证类"""
    
    def authenticate(self, request):
        """认证方法"""
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
            
        try:
            # 解析token
            token_type, token = auth_header.split(' ')
            if token_type.lower() != 'bearer':
                raise exceptions.AuthenticationFailed('无效的认证类型')
                
            # 验证token
            payload = jwt.decode(
                token,
                settings.JWT_SETTINGS['SECRET_KEY'],
                algorithms=[settings.JWT_SETTINGS['ALGORITHM']]
            )
            
            # 获取用户
            user = User.objects.get(id=payload['user_id'])
            return (user, token)
            
        except (ValueError, jwt.InvalidTokenError):
            raise exceptions.AuthenticationFailed('无效的认证信息')
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('用户不存在')
            
    @staticmethod
    def generate_token(user):
        """生成token"""
        # 访��令牌过期时间
        access_token_expires = datetime.utcnow() + timedelta(
            minutes=settings.JWT_SETTINGS['ACCESS_TOKEN_EXPIRE_MINUTES']
        )
        
        # 刷新令牌过期时间
        refresh_token_expires = datetime.utcnow() + timedelta(
            days=settings.JWT_SETTINGS['REFRESH_TOKEN_EXPIRE_DAYS']
        )
        
        # 生成访问令牌
        access_token_payload = {
            'user_id': user.id,
            'exp': access_token_expires,
            'type': 'access'
        }
        access_token = jwt.encode(
            access_token_payload,
            settings.JWT_SETTINGS['SECRET_KEY'],
            algorithm=settings.JWT_SETTINGS['ALGORITHM']
        )
        
        # 生成刷新令牌
        refresh_token_payload = {
            'user_id': user.id,
            'exp': refresh_token_expires,
            'type': 'refresh'
        }
        refresh_token = jwt.encode(
            refresh_token_payload,
            settings.JWT_SETTINGS['SECRET_KEY'],
            algorithm=settings.JWT_SETTINGS['ALGORITHM']
        )
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'expires_in': settings.JWT_SETTINGS['ACCESS_TOKEN_EXPIRE_MINUTES'] * 60
        }
        
    @staticmethod
    def refresh_token(refresh_token):
        """刷新token"""
        try:
            # 验证刷新令牌
            payload = jwt.decode(
                refresh_token,
                settings.JWT_SETTINGS['SECRET_KEY'],
                algorithms=[settings.JWT_SETTINGS['ALGORITHM']]
            )
            
            # 检查令牌类型
            if payload.get('type') != 'refresh':
                raise exceptions.AuthenticationFailed('无效的刷新令牌')
                
            # 获取用户
            user = User.objects.get(id=payload['user_id'])
            
            # 生成新的令牌
            return JWTAuthentication.generate_token(user)
            
        except (jwt.InvalidTokenError, User.DoesNotExist):
            raise exceptions.AuthenticationFailed('无效的刷新令牌') 