from rest_framework.response import Response
from rest_framework import status

def success_response(data=None, message='success', code=200):
    """成功响应"""
    return Response({
        'code': code,
        'message': message,
        'data': data
    }, status=status.HTTP_200_OK)
    
def error_response(message='error', code=500, status_code=None):
    """错误响应"""
    return Response({
        'code': code,
        'message': message
    }, status=status_code or status.HTTP_500_INTERNAL_SERVER_ERROR)
    
def validation_error(message='参数错误', code=400):
    """参数验证错误响应"""
    return Response({
        'code': code,
        'message': message
    }, status=status.HTTP_400_BAD_REQUEST)
    
def not_found_error(message='资源不存在', code=404):
    """资源不存在错误响应"""
    return Response({
        'code': code,
        'message': message
    }, status=status.HTTP_404_NOT_FOUND)
    
def permission_error(message='权限不足', code=403):
    """权限错误响应"""
    return Response({
        'code': code,
        'message': message
    }, status=status.HTTP_403_FORBIDDEN)
    
def unauthorized_error(message='未认证', code=401):
    """未认证错误响应"""
    return Response({
        'code': code,
        'message': message
    }, status=status.HTTP_401_UNAUTHORIZED) 