from django.conf.urls import include, url
from django.contrib import admin

from rest_framework import routers
import rest_framework_jwt.views

from web.views import (OpenPhotoViewSet, PageViewSet, WordpressCallback,
    ResourceViewSet, EventViewSet, EventSummaryView, ExportResources,
    SubmissionView)

router = routers.DefaultRouter()
router.register(r'openphotos', OpenPhotoViewSet)
router.register(r'pages', PageViewSet, base_name='Page')
router.register(r'resources', ResourceViewSet, base_name='Resource')
router.register(r'events', EventViewSet, base_name='Event')

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^api/submission/', SubmissionView.as_view()),
    url(r'^api/wp-callback/', WordpressCallback.as_view()),
    url(r'^api/events-summary/', EventSummaryView.as_view()),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', rest_framework_jwt.views.obtain_jwt_token),
    url(r'^api-token-refresh/', rest_framework_jwt.views.refresh_jwt_token),

    url(r'^export/resources/$', ExportResources.as_view(), name='resource_export'),
]
