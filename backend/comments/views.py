
# Create your views here.

from rest_framework.generics import ListCreateAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from captcha.helpers import captcha_image_url
from captcha.models import CaptchaStore
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import Comment
from .serializers import CommentSerializer


class CommentListCreateView(ListCreateAPIView):
    serializer_class = CommentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    ordering_fields = ['username', 'email', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        # Table on main page = root comments only (not replies)
        return Comment.objects.filter(parent__isnull=True).prefetch_related(
            'attachments',
            'replies',
            'replies__attachments',
            'replies__replies',
            'replies__replies__attachments',
        )


class CaptchaNewView(APIView):
    authentication_classes = []
    permission_classes = []
    def get(self, request):
        key = CaptchaStore.generate_key()
        return Response({
            'captcha_key': key,
            'image_url': captcha_image_url(key),
        })
