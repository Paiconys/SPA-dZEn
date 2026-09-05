from django.core.validators import RegexValidator
from rest_framework import serializers
from .models import Comment
import bleach

latin_alnum = RegexValidator(
    regex=r'^[a-zA-Z0-9]+$',
    message='Username may contain only latin letters and digits.',
)

    


class CommentSerializer(serializers.ModelSerializer):

    def validate_text(self, value):
        allowed_tags = ['a', 'code', 'i', 'strong']
        allowed_attributes = {'a': ['href', 'title']}

        parser = TagBalanceParser()
        parser.feed(value)
        parser.close()
        msg = parser.error_message()
        if msg:
            raise serializers.ValidationError(msg)


        return bleach.clean(
            value,
            tags=allowed_tags,
            attributes=allowed_attributes,
            strip=True,
        )


    username = serializers.CharField(
        max_length=250,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9]+$',
                message='Username may contain only latin letters and digits.',
            )
        ],
    )


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