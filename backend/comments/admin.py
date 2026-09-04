from django.contrib import admin
from .models import Comment, Attachment


class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'created_at', 'parent')
    list_filter = ('created_at',)
    search_fields = ('username', 'email', 'text')
    inlines = [AttachmentInline]


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'comment', 'file', 'uploaded_at')