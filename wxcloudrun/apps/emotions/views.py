from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
from wxcloudrun.apps.core.authentication import JWTAuthentication
from wxcloudrun.apps.core.utils.response import success_response, error_response
from wxcloudrun.apps.core.services.coze_service import coze_service, CozeServiceError
from .models import EmotionRecord
from .serializers import EmotionRecordSerializer
import logging

logger = logging.getLogger(__name__)

class EmotionViewSet(viewsets.ModelViewSet):
    """情绪记录视图集"""
    serializer_class = EmotionRecordSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """获取用户的情绪记录"""
        return EmotionRecord.objects.filter(
            user=self.request.user
        ).select_related('user').order_by('-created_at')
    
    @transaction.atomic    
    def perform_create(self, serializer):
        """创建情绪记录"""
        try:
            serializer.save(user=self.request.user)
        except Exception as e:
            logger.error(f"创建情绪记录失败: {str(e)}")
            raise ValidationError(f"创建情绪记录失败: {str(e)}")
    
    @action(detail=False, methods=['post'])
    def generate_photo(self, request):
        """生成情绪照片"""
        try:
            # 参数验证
            text = request.data.get('text')
            style = request.data.get('style')
            
            if not text:
                return error_response('请提供情绪描述文本', code=400)
            
            if len(text) > 500:
                return error_response('情绪描述文本过长，请控制在500字以内', code=400)
                
            # 调用COZE服务生成照片
            result = coze_service.generate_emotion_photo(text, style)
            
            # 记录生成历史
            with transaction.atomic():
                emotion_record = EmotionRecord.objects.create(
                    user=request.user,
                    content=text,
                    photo_url=result.get('photo_url'),
                    photo_style=style
                )
            
            return success_response({
                'record_id': emotion_record.id,
                'photo_url': result.get('photo_url'),
                'created_at': emotion_record.created_at
            })
            
        except CozeServiceError as e:
            logger.error(f"生成情绪照片失败: {str(e)}")
            return error_response(f"生成情绪照片失败: {str(e)}", code=500)
        except Exception as e:
            logger.error(f"处理请求失败: {str(e)}")
            return error_response('服务器内部错误', code=500)
            
    @action(detail=False, methods=['post'])
    def generate_curve(self, request):
        """生成情绪曲线"""
        try:
            # 参数验证
            emotions = request.data.get('emotions')
            
            if not emotions:
                return error_response('请提供情绪数据', code=400)
                
            if not isinstance(emotions, list):
                return error_response('情绪数据格式错误', code=400)
                
            if len(emotions) > 30:
                return error_response('情绪数据过多，请控制在30条以内', code=400)
                
            # 调用COZE服务生成曲线
            result = coze_service.generate_emotion_curve(emotions)
            
            return success_response({
                'curve_url': result.get('curve_url'),
                'analysis': result.get('analysis')
            })
            
        except CozeServiceError as e:
            logger.error(f"生成情绪曲线失败: {str(e)}")
            return error_response(f"生成情绪曲线失败: {str(e)}", code=500)
        except Exception as e:
            logger.error(f"处理请求失败: {str(e)}")
            return error_response('服务器内部错误', code=500)
            
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """��取情绪统计数据"""
        try:
            # 参数验证
            start_date = request.query_params.get('start_date')
            end_date = request.query_params.get('end_date')
            
            if not start_date or not end_date:
                return error_response('请提供开始和结束日期', code=400)
                
            try:
                start_date = timezone.datetime.strptime(start_date, '%Y-%m-%d')
                end_date = timezone.datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                return error_response('日期格式错误，请使用YYYY-MM-DD格式', code=400)
                
            if start_date > end_date:
                return error_response('开始日期不能晚于结束日期', code=400)
                
            if (end_date - start_date).days > 90:
                return error_response('时间范围不能超过90天', code=400)
            
            # 查询情绪记录
            queryset = self.get_queryset().filter(
                created_at__date__gte=start_date,
                created_at__date__lte=end_date
            )
            
            # 序列化数据
            serializer = self.get_serializer(queryset, many=True)
            
            # 统计数据
            total_count = queryset.count()
            emotion_levels = queryset.values_list('emotion_level', flat=True)
            
            statistics = {
                'total_count': total_count,
                'average_level': sum(emotion_levels) / total_count if total_count > 0 else 0,
                'records': serializer.data
            }
            
            return success_response(statistics)
            
        except Exception as e:
            logger.error(f"获取统计数据失败: {str(e)}")
            return error_response('服务器内部错误', code=500) 