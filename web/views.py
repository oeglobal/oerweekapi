# from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.permissions import AllowAny

from .models import OpenPhoto
from .serializers import OpenPhotoSerializer

class OpenPhotoViewSet(viewsets.ModelViewSet):
    permission_classes = (AllowAny,)

    queryset = OpenPhoto.objects.all()
    serializer_class = OpenPhotoSerializer

    def list(self, request):
        return super().list(self, request)
