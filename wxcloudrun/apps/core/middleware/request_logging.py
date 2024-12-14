import json
import logging
import time
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger('apps.core')

class RequestLoggingMiddleware(MiddlewareMixin):
    """请求日志中间件"""

    def process_request(self, request):
        """处理请求"""
        request.start_time = time.time()
        
        # 记录请求信息
        logger.info(
            'Request: %s %s\nHeaders: %s\nBody: %s',
            request.method,
            request.path,
            dict(request.headers),
            self._get_request_body(request)
        )
        
    def process_response(self, request, response):
        """处理响应"""
        # 计算请求耗时
        duration = time.time() - getattr(request, 'start_time', time.time())
        
        # 记录响应信息
        logger.info(
            'Response: %s %s\nStatus: %d\nDuration: %.3fs\nBody: %s',
            request.method,
            request.path,
            response.status_code,
            duration,
            self._get_response_body(response)
        )
        
        return response
        
    def _get_request_body(self, request):
        """获取请求体"""
        try:
            if request.body:
                return json.loads(request.body)
            return None
        except Exception:
            return None
            
    def _get_response_body(self, response):
        """获取响应体"""
        try:
            if hasattr(response, 'content'):
                return json.loads(response.content)
            return None
        except Exception:
            return None 