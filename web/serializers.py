from rest_framework import serializers

from .models import OpenPhoto

class OpenPhotoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OpenPhoto
        fields = ('id', 'title', 'url', 'country', 'city', 'status')
        read_only_fields = ('status',)
