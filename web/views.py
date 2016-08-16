import arrow
import xlwt
import urllib.parse
import json
from itertools import groupby
from datetime import datetime

from django.views.generic import View
from django.http import HttpResponse
from django.db.models import Q

from braces.views import LoginRequiredMixin

from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination

from .importer import import_resource, import_openphoto, import_submission
from .utils import send_submission_email
from .models import OpenPhoto, Page, Resource
from .serializers import (OpenPhotoSerializer, AuthenticatedOpenPhotoSerializer,
    PageSerializer, ResourceSerializer)

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 10000

class CustomResultsSetPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 1000


class OpenPhotoViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    queryset = OpenPhoto.objects.filter(post_status='publish',).order_by('?')
    pagination_class = LargeResultsSetPagination

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'POST'] and self.request.user.is_authenticated():
            return AuthenticatedOpenPhotoSerializer

        return OpenPhotoSerializer

class PageViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = PageSerializer

    def get_queryset(self):
        queryset = Page.objects.all()
        if self.request.GET.get('slug'):
            queryset = queryset.filter(slug=self.request.GET.get('slug'))

        return queryset

class WordpressCallback(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None):
        post_type = request.GET.get('post_type')
        if post_type:
            if post_type == 'openphoto':
                import_openphoto(post_id=request.GET.get('post_id'))
            else:
                import_resource(post_type=request.GET.get('post_type'),
                                post_id=request.GET.get('post_id'))

        return Response('OK')

class SubmissionView(APIView):
    def post(self, request, format=None):
        print(request.data)
        resource = import_submission(data=request.data)

        send_submission_email(resource)

        return Response(json.dumps(request.data), content_type='application/json')

class ResourceEventMixin(generics.GenericAPIView):
    def get_queryset(self):
        if self.request.GET.get('slug'):
            self.queryset = self.queryset.filter(slug=self.request.GET.get('slug'))

        if self.request.GET.get('year'):
            year = self.request.GET.get('year', '2016')
            self.queryset = self.queryset.filter(created__year=year)

        return self.queryset

class ResourceViewSet(ResourceEventMixin, viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ResourceSerializer

    def get_queryset(self):
        self.queryset = Resource.objects.filter(
                        post_status='publish',
                        post_type__in=['resource', 'project']
                    )
        super().get_queryset()

        return self.queryset

class EventViewSet(ResourceEventMixin, viewsets.ModelViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    serializer_class = ResourceSerializer
    pagination_class = CustomResultsSetPagination

    def get_queryset(self):
        self.queryset = Resource.objects.filter(
                        post_status='publish',
                        post_type__in=['event']
                    )
        super().get_queryset()

        if self.request.GET.get('event_type') == 'local':
            self.queryset = self.queryset \
                                .filter(created__year=2016) \
                                .exclude(Q(country='') | Q(event_type__in=('webinar', 'online')))

        if self.request.GET.get('event_type') == 'online':
            self.queryset = self.queryset \
                                .filter(created__year=2016,
                                        event_type__in=('webinar', 'online'))

        if self.request.GET.get('date'):
            date = arrow.get(self.request.GET.get('date'))
            self.queryset = self.queryset.filter(event_time__year=date.year,
                                                 event_time__month=date.month,
                                                 event_time__day=date.day)

        return self.queryset

class EventSummaryView(APIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request, format=None):
        summary = {}

        country_events = Resource.objects \
                            .filter(post_type='event',
                                    created__year=2016) \
                            .exclude(country='',
                                     event_type__in=('webinar', '')) \
                            .order_by('country')

        country_groups = []

        for k, g in groupby(country_events, lambda event: event.country):
            items = list(g)
            events = []
            for event in items:
                serialized = ResourceSerializer(event, context={'request': request})
                events.append(serialized.data)
            country_groups.append(events)

        summary['local_events'] = country_groups

        return Response(summary)

class ExportResources(LoginRequiredMixin, View):
    def get(self, request):
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename=oerweek-resources.xls'

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        datetime_style = xlwt.easyxf(num_format_str='dd/mm/yyyy hh:mm')

        wb = xlwt.Workbook(encoding='utf-8')
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
        ]

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num][0], font_style)
            ws.col(col_num).width = columns[col_num][1]

        font_style = xlwt.XFStyle()
        font_style.alignment.wrap = 1

        for resource in Resource.objects.filter(post_status='publish'):
            row_num += 1

            event_time = ''
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
            ]

            for col_num in range(len(row)):
                if isinstance(row[col_num], datetime):
                    ws.write(row_num, col_num, row[col_num], datetime_style)
                else:
                    ws.write(row_num, col_num, row[col_num], font_style)

        wb.save(response)
        return response
