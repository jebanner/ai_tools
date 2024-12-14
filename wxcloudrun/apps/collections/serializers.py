from rest_framework import serializers
from .models import Collection

class CollectionSerializer(serializers.ModelSerializer):
    """收藏记录序列化器"""
    tags_list = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = ['id', 'title', 'content', 'url', 'summary', 'tags', 'tags_list', 'created_at']
        read_only_fields = ['id', 'summary', 'tags', 'created_at']

    def get_tags_list(self, obj):
        """将tags字符串转换为列表"""
        if obj.tags:
            return [tag.strip() for tag in obj.tags.split(',')]
        return []

class CollectionCreateSerializer(serializers.ModelSerializer):
    """创建收藏记录序列化器"""
    class Meta:
        model = Collection
        fields = ['title', 'content', 'url']

    def create(self, validated_data):
        user = self.context['request'].user
        return Collection.objects.create(user=user, **validated_data) 