from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action
from .models import Film
from .serializers import FilmSerializer
from django_pandas.io import read_frame


class FilmViewSet(viewsets.ModelViewSet):
    queryset = Film.objects.all()
    serializer_class = FilmSerializer

    # http://127.0.0.1:8000/api/films/search_by_title/?title=Batmen
    @action(detail=False, methods=['get'])
    def search_by_title(self, request):
        title = request.query_params.get('title', None)
        try:
            df = read_frame(self.queryset)
            df = df[df['title'] == title]
            return Response(df.to_dict('records'))
        except ValueError:
            return Response([])

    # http://127.0.0.1:8000/api/films/filter_rating/?min=4&max=5
    @action(detail=False, methods=['get'])
    def filter_rating(self, request):
        min = request.query_params.get('min', None)
        max = request.query_params.get('max', None)
        try:
            df = read_frame(self.queryset)
            df = df[df['rating'].between(int(min), int(max))]
            return Response(df.to_dict('records'))
        except ValueError:
            return Response([])

    # http://127.0.0.1:8000/api/films/filter_year/?year=2023
    @action(detail=False, methods=['get'])
    def filter_year(self, request):
        year = request.query_params.get('year', None)
        try:
            df = read_frame(self.queryset)
            df = df[df['year'] > int(year)]
            return Response(df.to_dict('records'))
        except ValueError:
            return Response([])
