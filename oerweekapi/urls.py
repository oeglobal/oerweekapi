from django.conf.urls import include, url
from django.contrib import admin

from rest_framework import routers
import rest_framework_jwt.views

from web.views import OpenPhotoViewSet

router = routers.DefaultRouter()
router.register(r'openphotos', OpenPhotoViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', rest_framework_jwt.views.obtain_jwt_token),
    url(r'^api-token-refresh/', rest_framework_jwt.views.refresh_jwt_token),
]
