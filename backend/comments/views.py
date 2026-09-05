
# Create your views here.

from rest_framework.generics import ListCreateAPIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from .models import Comment
from .serializers import CommentSerializer


class CommentListCreateView(ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    ordering_fields = ['username', 'email', 'created_at']
    ordering = ['-created_at']



