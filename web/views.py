# from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination

from .importer import import_resource, import_openphoto
from .models import OpenPhoto, Page, Resource
from .serializers import (OpenPhotoSerializer, AuthenticatedOpenPhotoSerializer,
    PageSerializer, ResourceSerializer)

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000

class OpenPhotoViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = OpenPhoto.objects.filter(post_status='publish',)
    pagination_class = LargeResultsSetPagination

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
        post_type = request.GET.get('post_type')
        if post_type:
            if post_type == 'openphoto':
                import_openphoto(post_id=request.GET.get('post_id'))
            else:
                import_resource(post_type=request.GET.get('post_type'),
                                post_id=request.GET.get('post_id'))

        return Response('OK')

class ResourceEventMixin(generics.GenericAPIView):
    def get_queryset(self):
        if self.request.GET.get('slug'):
            self.queryset = self.queryset.filter(slug=self.request.GET.get('slug'))

        if self.request.GET.get('year'):
            year = self.request.GET.get('year', '2016')
            self.queryset = self.queryset.filter(created__year=year)

        return self.queryset

class ResourceViewSet(ResourceEventMixin, viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ResourceSerializer

    def get_queryset(self):
        self.queryset = Resource.objects.filter(
                        post_status='publish',
                        post_type__in=['resource', 'project']
                    )
        super().get_queryset()

        return self.queryset

class EventViewSet(ResourceEventMixin, viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ResourceSerializer

    def get_queryset(self):
        self.queryset = Resource.objects.filter(
                        post_status='publish',
                        post_type__in=['event']
                    )
        super().get_queryset()

        return self.queryset
