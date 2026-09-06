from asgiref.sync import async_to_sync
from captcha.models import CaptchaStore
from channels.layers import get_channel_layer
from rest_framework import serializers

from .html_utils import sanitize_comment_html
from .models import Attachment, Comment
from .validators import resize_image_if_needed


class AttachmentSerializer(serializers.ModelSerializer):
    # Relative /media/... so Vite proxy works (absolute http://web:8000 breaks in browser)
    file = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ['id', 'file', 'uploaded_at']
        read_only_fields = ['id', 'file', 'uploaded_at']

    def get_file(self, obj):
        if not obj.file:
            return ''
        return obj.file.url


class CommentSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    replies = serializers.SerializerMethodField()
    file = serializers.FileField(required=False, write_only=True)
    captcha_key = serializers.CharField(write_only=True)
    captcha = serializers.CharField(write_only=True)

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
            'attachments',
            'replies',
            'file',
            'captcha_key',
            'captcha',
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'homepage': {'required': False, 'allow_blank': True},
        }

    def get_replies(self, obj):
        children = obj.replies.all().order_by('created_at')
        return CommentSerializer(children, many=True, context=self.context).data

    def validate(self, attrs):
        key = attrs.pop('captcha_key', None)
        value = attrs.pop('captcha', None)

        try:
            store = CaptchaStore.objects.get(hashkey=key)
        except CaptchaStore.DoesNotExist:
            raise serializers.ValidationError({'captcha': 'Invalid or expired captcha.'})

        if store.response.lower() != str(value).lower().strip():
            store.delete()
            raise serializers.ValidationError({'captcha': 'Invalid captcha.'})

        store.delete()
        return attrs

    def validate_text(self, value):
        try:
            return sanitize_comment_html(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc)) from exc

    def validate_file(self, value):
        return resize_image_if_needed(value)

    def create(self, validated_data):
        upload = validated_data.pop('file', None)
        comment = Comment.objects.create(**validated_data)
        if upload is not None:
            attachment = Attachment(comment=comment, file=upload)
            attachment.full_clean()
            attachment.save()

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'comments',
            {
                'type': 'comment.created',
                'data': CommentSerializer(comment).data,
            },
        )
        return comment
