# from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .importer import import_project
from .models import OpenPhoto, Page, Resource
from .serializers import (OpenPhotoSerializer, AuthenticatedOpenPhotoSerializer,
    PageSerializer, ResourceSerializer)

class OpenPhotoViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = OpenPhoto.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'POST'] and self.request.user.is_authenticated():
            return AuthenticatedOpenPhotoSerializer

        return OpenPhotoSerializer

class PageViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = PageSerializer

    def get_queryset(self):
        queryset = Page.objects.all()
        if self.request.GET.get('slug'):
            queryset = queryset.filter(slug=self.request.GET.get('slug'))

        return queryset

class WordpressCallback(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None):
        if request.GET.get('post_type'):
            import_project(request.GET.get('post_id'))

        return Response('OK')

class ResourceViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ResourceSerializer

    def get_queryset(self):
        queryset = Resource.objects.filter(post_status='publish', created__year=2016)
        if self.request.GET.get('slug'):
            queryset = queryset.filter(slug=self.request.GET.get('slug'))

        return queryset
