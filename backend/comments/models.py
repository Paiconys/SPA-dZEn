from django.db import models



# Create your models here.

class Comment(models.Model):

    username = models.CharField(max_length=250)
    email = models.EmailField()
    homepage = models.URLField(blank=True)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
    'self', 
    on_delete=models.CASCADE,   
    null=True, 
    blank=True, 
    related_name='replies'
    )

    def __str__(self):
        return f'{self.username}: {self.text[:50]}'



class Attachment(models.Model):
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='attachments',
    )
    file = models.FileField(upload_to='attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Attachment for {self.comment_id}'