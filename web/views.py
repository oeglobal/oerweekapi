import arrow
import xlwt
import urllib.parse
import twitter

from itertools import groupby
from datetime import datetime

from django.views.generic import View
from django.http import HttpResponse
from django.db.models import Q
from django.conf import settings
from django.core.cache import cache

from braces.views import LoginRequiredMixin

from rest_framework import permissions, viewsets, generics, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Page, Resource, ResourceImage, EmailTemplate
from .serializers import (
    PageSerializer,
    ResourceSerializer,
    SubmissionResourceSerializer,
    AdminSubmissionResourceSerializer,
    EmailTemplateSerializer,
    ResourceImageSerializer,
)


class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = "page_size"
    max_page_size = 10000
    page_query_param = "page['number']"


class CustomResultsSetPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = "page_size"
    max_page_size = 1000
    page_query_param = "page['number']"


class PageViewSet(viewsets.ModelViewSet):
    serializer_class = PageSerializer

    def get_queryset(self):
        queryset = Page.objects.all()
        if self.request.GET.get("slug"):
            queryset = queryset.filter(slug=self.request.GET.get("slug"))

        return queryset


class SubmissionPermission(permissions.BasePermission):
    message = "For changing submissions, you have to be logged-in"

    def has_permission(self, request, view):
        # We allow POST, since it's a `add` method, so users can submit form.
        if request.method == "POST" or request.method == "OPTIONS":
            return True

        if request.user.is_authenticated:
            return True

        return False


class SubmissionViewSet(viewsets.ModelViewSet):
    permission_classes = (SubmissionPermission,)
    pagination_class = CustomResultsSetPagination
    resource_name = "submission"

    def get_serializer_class(self):
        if self.request.user.is_superuser:
            return AdminSubmissionResourceSerializer

        return SubmissionResourceSerializer

    def get_queryset(self):
        queryset = Resource.objects.filter(
            created__gte=arrow.get(settings.OEW_CFP_OPEN).datetime
        ).order_by("-created")
        if self.request.user.is_staff:
            return queryset

        return queryset.filter(email__iexact=self.request.user.email)


class ResourceEventMixin(generics.GenericAPIView):
    filterset_fields = ("slug", "form_language")

    def get_queryset(self, queryset):
        if self.request.GET.get("year"):
            year = self.request.GET.get("year", settings.OEW_YEAR)
            queryset = queryset.filter(year=year)

        if self.request.GET.get("opentags"):
            opentags = self.request.GET.get("opentags", "").split(",")
            queryset = queryset.filter(opentags__contains=opentags)

        return queryset


class ResourceViewSet(ResourceEventMixin, viewsets.ModelViewSet):
    serializer_class = ResourceSerializer

    def get_queryset(self):
        queryset = Resource.objects.filter(
            post_status="publish", post_type__in=["resource", "project"]
        ).order_by("-id")

        return super().get_queryset(queryset)


class EventViewSet(ResourceEventMixin, viewsets.ModelViewSet):
    serializer_class = ResourceSerializer
    resource_name = "event"

    def get_queryset(self):
        queryset = Resource.objects.filter(
            post_status="publish", post_type__in=["event"]
        )
        queryset = super().get_queryset(queryset)

        if self.request.GET.get("special") == "current":
            current_time = arrow.now().shift(hours=-1)
            queryset = Resource.objects.filter(
                event_type="online",
                event_time__gte=current_time.datetime,
                post_status="publish",
            ).order_by("event_time")[:8]
            return queryset

        event_type = self.request.GET.get("event_type")
        if event_type and len(event_type) == 1:
            event_type = event_type.pop()

        if event_type == "local":
            queryset = queryset.filter(year=settings.OEW_YEAR).exclude(
                Q(country="") | Q(event_type__in=("webinar", "online"))
            )

        if event_type == "online":
            queryset = queryset.filter(
                year=settings.OEW_YEAR,
                event_type__in=("webinar", "online", "other_online"),
            )

        if self.request.GET.get("date"):
            if self.request.GET.get("date") == "other":
                queryset = queryset.filter(event_time__month=3).exclude(
                    event_time__range=settings.OEW_RANGE
                )
            else:
                date = arrow.get(self.request.GET.get("date"))
                queryset = queryset.filter(
                    event_time__year=date.year,
                    event_time__month=date.month,
                    event_time__day=date.day,
                )

        return queryset.order_by("event_time")


class EventSummaryView(APIView):
    def get(self, request, format=None):
        summary = {}

        country_events = (
            Resource.objects.filter(post_type="event", modified__year=settings.OEW_YEAR)
            .exclude(country="", event_type__in=("webinar", ""))
            .order_by("country")
        )

        country_groups = []

        for k, g in groupby(country_events, lambda event: event.country):
            items = list(g)
            events = []
            for event in items:
                serialized = ResourceSerializer(event, context={"request": request})
                events.append(serialized.data)
            country_groups.append(events)

        summary["local_events"] = country_groups

        return Response(summary)


class ExportResources(LoginRequiredMixin, View):
    def get(self, request):
        response = HttpResponse(content_type="application/ms-excel")
        response["Content-Disposition"] = "attachment; filename=oerweek-resources.xls"

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        datetime_style = xlwt.easyxf(num_format_str="dd/mm/yyyy hh:mm")

        wb = xlwt.Workbook(encoding="utf-8")
        ws = wb.add_sheet("Resources")

        row_num = 0

        columns = [
            (u"ID", 2000),
            (u"Resource Type", 6000),
            (u"Title", 6000),
            (u"Organization", 8000),
            (u"Contact name", 8000),
            (u"Email", 8000),
            (u"OEW URL", 8000),
            (u"Resources URL", 8000),
            (u"Event Type", 8000),
            (u"Date and Time", 8000),
            (u"Country", 8000),
            (u"City", 8000),
            (u"Language", 8000),
            (u"Twitter", 8000),
            (u"Tags", 8000),
        ]

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num][0], font_style)
            ws.col(col_num).width = columns[col_num][1]

        font_style = xlwt.XFStyle()
        font_style.alignment.wrap = 1

        for resource in Resource.objects.filter(
            post_status="publish", year=settings.OEW_YEAR
        ):
            row_num += 1

            event_time = ""
            if resource.event_time:
                # event_time = resource.event_time.strftime('%Y-%m-%d %H:%M')
                event_time = resource.event_time.replace(tzinfo=None)

            row = [
                resource.post_id,
                resource.post_type,
                urllib.parse.unquote(resource.title),
                resource.institution,
                resource.contact,
                resource.email,
                resource.get_full_url(),
                resource.link,
                resource.event_type,
                event_time,
                resource.country,
                resource.city,
                resource.form_language,
                resource.twitter,
                ", ".join(resource.opentags or []),
            ]

            for col_num in range(len(row)):
                if isinstance(row[col_num], datetime):
                    ws.write(row_num, col_num, row[col_num], datetime_style)
                else:
                    ws.write(row_num, col_num, row[col_num], font_style)

        wb.save(response)
        return response


class TwitterSearchResults(APIView):
    def get(self, request, format=None):
        if cache.get("twitter", None):
            results = cache.get("twitter")
            return Response(results)

        twitter_api = twitter.Api(
            consumer_key=settings.TWITTER_API_KEY,
            consumer_secret=settings.TWITTER_API_SECRET,
            access_token_key=settings.TWITTER_ACCESS_TOKEN_KEY,
            access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET,
        )

        api_results = twitter_api.GetSearch(
            raw_query="q=%23openeducationwk%2C%20OR%20%23oeglobal&result_type=mixed&count=100"
        )

        results = []
        for res in api_results:
            if not res.retweeted_status:
                results.append(
                    {"screen_name": res.user.screen_name, "id_str": res.id_str}
                )
        results = results[:4]

        cache.set("twitter", results, 60 * 5)
        return Response(results)


class EmailTemplateView(viewsets.ReadOnlyModelViewSet):
    model = EmailTemplate
    serializer_class = EmailTemplateSerializer
    queryset = EmailTemplate.objects.all().order_by("id")


class ResourceImageViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (SubmissionPermission,)
    model = ResourceImage
    serializer_class = ResourceImageSerializer
    queryset = ResourceImage.objects.all().order_by("-id")


class RequestAccessView(APIView):
    permission_classes = (SubmissionPermission,)

    def post(self, request, format=None):
        email = request.data.get("email")

        try:
            print(email)
            resource = Resource.objects.filter(email=email)[0]
            resource.send_new_account_email(force=True)

        except IndexError:
            return Response({"status": "invalid_email"})

        return Response({"status": "ok"})
