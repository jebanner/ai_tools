from rest_framework.views import exception_handler
from rest_framework.exceptions import APIException
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.db import DatabaseError
from .response import error_response, not_found_error, permission_error

def custom_exception_handler(exc, context):
    """自定义异常处理"""
    # 先调用REST framework的默认异常处理
    response = exception_handler(exc, context)
    
    if response is not None:
        # 处理REST framework的异常
        return error_response(
            message=str(exc),
            code=response.status_code,
            status_code=response.status_code
        )
        
    if isinstance(exc, Http404):
        # 处理404错误
        return not_found_error()
        
    if isinstance(exc, PermissionDenied):
        # 处理权限错误
        return permission_error()
        
    if isinstance(exc, DatabaseError):
        # 处理数据库错误
        return error_response('数据库错误')
        
    # 处理其他未知错误
    return error_response(str(exc))
    
class BusinessError(APIException):
    """业务异常"""
    
    def __init__(self, message='业务处理失败', code=400):
        self.status_code = code
        self.default_detail = message
        self.default_code = 'business_error'
        super().__init__(detail=message)
        
class ValidationError(APIException):
    """参数验证异常"""
    
    def __init__(self, message='参数验证失败', code=400):
        self.status_code = code
        self.default_detail = message
        self.default_code = 'validation_error'
        super().__init__(detail=message)
        
class AuthenticationError(APIException):
    """认证异常"""
    
    def __init__(self, message='认证失败', code=401):
        self.status_code = code
        self.default_detail = message
        self.default_code = 'authentication_error'
        super().__init__(detail=message)
        
class PermissionError(APIException):
    """权限异常"""
    
    def __init__(self, message='权限不足', code=403):
        self.status_code = code
        self.default_detail = message
        self.default_code = 'permission_error'
        super().__init__(detail=message)
        
class NotFoundError(APIException):
    """资源不存在异常"""
    
    def __init__(self, message='资源不存在', code=404):
        self.status_code = code
        self.default_detail = message
        self.default_code = 'not_found_error'
        super().__init__(detail=message) 