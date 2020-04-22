from django.db import models
from rest_framework import generics

from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Movie, Person
from .serializers import (
    MovieListSerializer,
    MovieDetailSerializer,
    ReviewCreateSerializer,
    RatingCreateSerializer,
    PersonListSerializer,
    PersonDetailSerializer,
)
from .services import get_client_ip_from_request


class MovieListView(APIView):
    """Вывод списка фильмов"""

    def get(self, request):
        movies = Movie.objects.filter(draft=False).annotate(
            rating_user=models.Count("ratings", filter=models.Q(ratings__ip=get_client_ip_from_request(request)))
        ).annotate(
            average_rating=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings'))
        )
        serializer = MovieListSerializer(movies, many=True)
        return Response(serializer.data)


class MovieDetailView(APIView):
    """Вывод подробностей фильмов"""

    def get(self, request, pk):
        movie = Movie.objects.get(id=pk, draft=False)
        serializer = MovieDetailSerializer(movie)
        return Response(serializer.data)


class PersonListView(generics.ListAPIView):
    """Вывод списка персоналий"""

    queryset = Person.objects.all()
    serializer_class = PersonListSerializer


class PersonDetailView(generics.RetrieveAPIView):
    """Вывод деталей персоналия"""

    queryset = Person.objects.all()
    serializer_class = PersonDetailSerializer


class ReviewCreateView(APIView):
    """Вывод отзывов к фильму"""

    def post(self, request):
        review = ReviewCreateSerializer(data=request.data)
        if review.is_valid():
            review.save()
        return Response(status=201)


class RatingCreateView(APIView):
    """Добавление рейтинга к фильму."""

    def post(self, request):
        serializer = RatingCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ip=get_client_ip_from_request(request))
            return Response(status=201)
        return Response(status=400)
