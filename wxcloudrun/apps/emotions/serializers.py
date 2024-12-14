from rest_framework import serializers
from .models import EmotionRecord

class EmotionRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmotionRecord
        fields = ['id', 'emotion_type', 'emotion_level', 'description', 'ai_analysis', 'created_at']
        read_only_fields = ['id', 'ai_analysis', 'created_at']

class EmotionRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmotionRecord
        fields = ['emotion_type', 'emotion_level', 'description']

    def create(self, validated_data):
        user = self.context['request'].user
        return EmotionRecord.objects.create(user=user, **validated_data) 