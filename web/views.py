# from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import OpenPhoto, Page
from .serializers import OpenPhotoSerializer, AuthenticatedOpenPhotoSerializer, PageSerializer

class OpenPhotoViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = OpenPhoto.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'POST'] and self.request.user.is_authenticated():
            return AuthenticatedOpenPhotoSerializer

        return OpenPhotoSerializer

class PageViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = Page.objects.all()
    serializer_class = PageSerializer
