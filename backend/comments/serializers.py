from rest_framework import serializers
from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            'id',
            'username',
            'email',
            'homepage',
            'text',
            'parent',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']