from django.db import models

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets

from .models import Movie, Person, Review, Rating
from . import serializers
from .services import get_client_ip_from_request
from .filters import MovieFilter
from .permissions import IsEmailOwner, IsIpOwner


class MovieViewSet(viewsets.ModelViewSet):
    """Вьюсет для отображения фильмов"""
    queryset = Movie.objects.filter(draft=False)
    serializer_class = serializers.MovieListSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = MovieFilter
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'update', 'partial_update', 'delete'):
            return serializers.MovieDetailSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'delete'):
            self.permission_classes = (permissions.IsAdminUser,)
        return [permission() for permission in self.permission_classes]

    def get_queryset(self):
        queryset = Movie.objects.filter(draft=False).annotate(
            rating_user=models.Count("ratings", filter=models.Q(ratings__ip=get_client_ip_from_request(self.request)))
        ).annotate(
            average_rating=models.Sum(models.F('ratings__star')) / models.Count(models.F('ratings'))
        )
        return queryset


class PersonViewSet(viewsets.ModelViewSet):
    """Вьюсет для отображения персоналий"""
    queryset = Person.objects.all()
    serializer_class = serializers.PersonListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'update', 'partial_update', 'delete'):
            return serializers.PersonDetailSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'delete'):
            self.permission_classes = (permissions.IsAdminUser,)
        return [permission() for permission in self.permission_classes]


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для отображения отзывов"""
    queryset = Review.objects.all()
    serializer_class = serializers.ReviewSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_serializer_class(self):
        if self.action in ('retrieve', 'update', 'partial_update', 'delete'):
            return serializers.ReviewCreateSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in ('update', 'partial_update'):
            self.permission_classes = (IsEmailOwner,)
        elif self.action == 'delete':
            self.permission_classes = (IsEmailOwner, permissions.IsAdmin)
        return [permission() for permission in self.permission_classes]


class RatingViewSet(viewsets.ModelViewSet):
    """Вьюсет для отображения рейтингов"""
    queryset = Rating.objects.all()
    serializer_class = serializers.RatingSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(ip=get_client_ip_from_request(self.request))

    def get_permissions(self):
        if self.action in ('update', 'partial_update', 'delete'):
            self.permission_classes = (IsIpOwner,)
        return [permission() for permission in self.permission_classes]
