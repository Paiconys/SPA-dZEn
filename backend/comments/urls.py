from django.urls import path

from .views import CaptchaNewView, CommentListCreateView

urlpatterns = [
    path('comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('captcha/', CaptchaNewView.as_view(), name='captcha-new'),
]