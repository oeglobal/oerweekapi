# from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import OpenPhoto
from .serializers import OpenPhotoSerializer, AuthenticatedOpenPhotoSerializer

class OpenPhotoViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = OpenPhoto.objects.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'POST'] and self.request.user.is_authenticated():
            return AuthenticatedOpenPhotoSerializer

        return OpenPhotoSerializer

    def list(self, request):
        return super().list(self, request)

    # def update(self, request, pk=None):
    #     if request.user.is_authenticated():
    #         obj = super().update(request, pk)
    #         import ipdb; ipdb.set_trace()

