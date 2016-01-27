from rest_framework import serializers

from .models import OpenPhoto, Page

class OpenPhotoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OpenPhoto
        fields = ('id', 'title', 'url', 'country', 'city', 'status')
        read_only_fields = ('status', 'title')

    def save(self):
        super().save()

        if not self.instance.status:
            self.instance.status = 'new'
            self.instance.save()

        if not self.instance.title:
            self.instance.title = 'OpenPhoto #{}'.format(self.instance.id)
            self.instance.save()

        return self.instance

class AuthenticatedOpenPhotoSerializer(OpenPhotoSerializer):
    class Meta:
        model = OpenPhoto
        fields = ('id', 'title', 'url', 'country', 'city', 'status')
        read_only_fields = ('title',)

class PageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Page
        fields = ('id', 'title', 'slug', 'content')
