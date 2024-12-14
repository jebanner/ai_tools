from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count
from django.db.models.functions import TruncDate
from .models import CareerRecord
from .serializers import CareerRecordSerializer, CareerRecordCreateSerializer
from wxcloudrun.apps.core.utils.response import api_response
from wxcloudrun.apps.core.services.ai_service import AIService

class CareerRecordViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CareerRecordSerializer
    
    def get_queryset(self):
        return CareerRecord.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'create':
            return CareerRecordCreateSerializer
        return CareerRecordSerializer

    def perform_create(self, serializer):
        career_record = serializer.save()
        # 调用AI服务进行分析
        ai_service = AIService()
        analysis = ai_service.analyze_career(career_record.content)
        career_record.ai_analysis = analysis
        career_record.save()

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取职业发展记录统计数据"""
        records_by_date = self.get_queryset().annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        return api_response(data=list(records_by_date))

    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """按记录类型获取统计数据"""
        records_by_type = self.get_queryset().values('record_type').annotate(
            count=Count('id')
        ).order_by('record_type')
        
        return api_response(data=list(records_by_type)) 