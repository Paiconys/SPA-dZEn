
# Create your views here.

from rest_framework.generics import ListCreateAPIView

from .models import Comment
from .serializers import CommentSerializer


class CommentListCreateView(ListCreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    ordering_fields = ['username', 'email', 'created_at']
    ordering = ['-created_at']  # LIFO по умолчанию



