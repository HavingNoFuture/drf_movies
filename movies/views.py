from django.db import models

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions

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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class PersonListView(generics.ListAPIView):
    """Вывод списка персоналий"""
    queryset = Person.objects.all()
    serializer_class = PersonListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class PersonDetailView(generics.RetrieveAPIView):
    """Вывод деталей персоналия"""
    queryset = Person.objects.all()
    serializer_class = PersonDetailSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class ReviewCreateView(generics.CreateAPIView):
    """Создание  к фильму"""
    serializer_class = ReviewCreateSerializer
    permission_classes = (permissions.IsAuthenticated,)


class RatingCreateView(generics.CreateAPIView):
    """Добавление рейтинга к фильму."""
    serializer_class = RatingCreateSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(ip=get_client_ip_from_request(self.request))
