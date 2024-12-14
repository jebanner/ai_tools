import logging
import traceback
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('apps.core')

class ErrorHandlerMiddleware(MiddlewareMixin):
    """错误处理中间件"""

    def process_exception(self, request, exception):
        """处理异常"""
        # 记录错误日志
        logger.error(
            'Request error: %s\nTraceback:\n%s',
            str(exception),
            traceback.format_exc()
        )
        
        # 返回错误响应
        return JsonResponse({
            'code': 500,
            'message': '服务器内部错误'
        }, status=500) 