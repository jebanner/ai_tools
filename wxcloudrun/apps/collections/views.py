from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.db.models.functions import TruncDate
from django.db.models import Count
from .models import Collection
from .serializers import CollectionSerializer, CollectionCreateSerializer
from wxcloudrun.apps.core.utils.response import api_response
from wxcloudrun.apps.core.services.ai_service import AIService

class CollectionViewSet(viewsets.ModelViewSet):
    """智能收藏视图集"""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CollectionSerializer

    def get_queryset(self):
        return Collection.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return CollectionCreateSerializer
        return CollectionSerializer

    def perform_create(self, serializer):
        collection = serializer.save()
        # 调用AI服务生成摘要和标签
        ai_service = AIService()
        analysis = ai_service.generate_summary(collection.content)
        if analysis:
            collection.summary = analysis.get('summary', '')
            collection.tags = ','.join(analysis.get('tags', []))
            collection.save()

    @action(detail=False, methods=['get'])
    def search(self, request):
        """搜索收藏内容"""
        keyword = request.query_params.get('keyword', '')
        tag = request.query_params.get('tag', '')

        queryset = self.get_queryset()
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) |
                Q(content__icontains=keyword) |
                Q(summary__icontains=keyword)
            )
        if tag:
            queryset = queryset.filter(tags__icontains=tag)

        serializer = self.get_serializer(queryset, many=True)
        return api_response(data=serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """获取收藏统计数据"""
        collections_by_date = self.get_queryset().annotate(
            date=TruncDate('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')

        # 获取所有标签及其使用次数
        all_tags = {}
        for collection in self.get_queryset():
            if collection.tags:
                for tag in collection.tags.split(','):
                    tag = tag.strip()
                    all_tags[tag] = all_tags.get(tag, 0) + 1

        tags_stats = [{'tag': tag, 'count': count} 
                     for tag, count in sorted(all_tags.items(), 
                                           key=lambda x: x[1], 
                                           reverse=True)]

        return api_response(data={
            'by_date': list(collections_by_date),
            'tags': tags_stats
        }) 