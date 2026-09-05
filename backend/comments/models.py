from django.core.validators import RegexValidator
from django.db import models

from .validators import allowed_file_extensions, validate_txt_size

username_validator = RegexValidator(
    regex=r'^[a-zA-Z0-9]+$',
    message='Username may contain only latin letters and digits.',
)


class Comment(models.Model):
    username = models.CharField(max_length=250, validators=[username_validator])
    email = models.EmailField()
    homepage = models.URLField(blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
    )

    def __str__(self):
        return f'{self.username}: {self.text[:50]}'


class Attachment(models.Model):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='attachments',
    )
    file = models.FileField(
        upload_to='attachments/',
        validators=[allowed_file_extensions, validate_txt_size],
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Attachment for {self.comment_id}'
