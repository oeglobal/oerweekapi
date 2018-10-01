from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf import settings
from django.contrib import admin

from rest_framework import routers
import rest_framework_jwt.views

from web.views import (PageViewSet, ResourceViewSet, EventViewSet,
                       EventSummaryView, ExportResources, ResourceImageViewSet,
                       SubmissionViewSet, TwitterSearchResults, EmailTemplateView,
                       RequestAccessView)

router = routers.DefaultRouter(trailing_slash=False)
router.register(r'pages', PageViewSet, base_name='Page')
router.register(r'resource', ResourceViewSet, base_name='Resource')
router.register(r'resource-image', ResourceImageViewSet, base_name='ResourceImage')
router.register(r'event', EventViewSet, base_name='Event')
router.register(r'submission', SubmissionViewSet, base_name='Submission')
router.register(r'email-templates', EmailTemplateView)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    # url(r'^api/submission/', SubmissionView.as_view()),
    url(r'^api/events-summary/', EventSummaryView.as_view()),
    url(r'^api/twitter/', TwitterSearchResults.as_view()),
    url(r'^api/request-access/', RequestAccessView.as_view()),

    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api-token-auth/', rest_framework_jwt.views.obtain_jwt_token),
    url(r'^api-token-refresh/', rest_framework_jwt.views.refresh_jwt_token),

    url(r'^export/resources/$', ExportResources.as_view(), name='resource_export'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
