from rest_framework import serializers

from .models import OpenPhoto

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
