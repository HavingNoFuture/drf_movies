from django.db import models

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

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
from .filters import MovieFilter


class MovieListView(generics.ListAPIView):
    """Вывод списка фильмов"""
    serializer_class = MovieListSerializer
    filter_backends = (DjangoFilterBackend, )
    filterset_class = MovieFilter


    def get_queryset(self):
        queryset = Movie.objects.filter(draft=False).annotate(
            rating_user=models.Count("ratings", filter=models.Q(ratings__ip=get_client_ip_from_request(self.request)))
        ).annotate(
            average_rating=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings'))
        )
        return queryset


class MovieDetailView(generics.RetrieveAPIView):
    """Вывод подробностей фильмов"""
    queryset = Movie.objects.filter(draft=False)
    serializer_class = MovieDetailSerializer


class PersonListView(generics.ListAPIView):
    """Вывод списка персоналий"""
    queryset = Person.objects.all()
    serializer_class = PersonListSerializer


class PersonDetailView(generics.RetrieveAPIView):
    """Вывод деталей персоналия"""
    queryset = Person.objects.all()
    serializer_class = PersonDetailSerializer


class ReviewCreateView(generics.CreateAPIView):
    """Вывод отзывов к фильму"""
    serializer_class = ReviewCreateSerializer


class RatingCreateView(generics.CreateAPIView):
    """Добавление рейтинга к фильму."""
    serializer_class = RatingCreateSerializer

    def perform_create(self, serializer):
        serializer.save(ip=get_client_ip_from_request(self.request))

class Da(generics.CreateAPIView):
    pass
