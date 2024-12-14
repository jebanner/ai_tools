from rest_framework import serializers
from .models import CareerRecord

class CareerRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerRecord
        fields = ['id', 'title', 'content', 'record_type', 'ai_analysis', 'created_at']
        read_only_fields = ['id', 'ai_analysis', 'created_at']

class CareerRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerRecord
        fields = ['title', 'content', 'record_type']

    def create(self, validated_data):
        user = self.context['request'].user
        return CareerRecord.objects.create(user=user, **validated_data) 