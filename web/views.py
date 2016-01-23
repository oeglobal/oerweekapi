# from django.shortcuts import render

from rest_framework import viewsets

from .models import OpenPhoto
from .serializers import OpenPhotoSerializer

class OpenPhotoViewSet(viewsets.ModelViewSet):
    queryset = OpenPhoto.objects.all()
    serializer_class = OpenPhotoSerializer
