from django.views.generic import DetailView
from rest_framework import viewsets

from apps.users.permissions import IsModeratorOrReadOnly

from .models import Project
from .serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsModeratorOrReadOnly]
    filterset_fields = ["status", "is_featured"]
    search_fields = ["title", "short_description", "description", "location"]
    ordering_fields = ["created_at", "goal_amount", "raised_amount"]


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/detail.html"
    context_object_name = "project"
    slug_field = "slug"
