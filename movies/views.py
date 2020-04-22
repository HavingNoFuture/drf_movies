from django.contrib.auth import get_user_model
from rest_framework.fields import ReadOnlyField
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Movie
from .serializers import MovieListSerializer, MovieDetailSerializer, ReviewCreateSerializer, RatingCreateSerializer
from .services import get_client_ip_from_request

User = get_user_model()


class MovieListView(APIView):
    """Вывод списка фильмов"""

    def get(self, request):
        movies = Movie.objects.filter(draft=False)
        serializer = MovieListSerializer(movies, many=True)
        print(Movie.objects.filter(category__name='movies'))
        return Response(serializer.data)


class MovieDetailView(APIView):
    """Вывод подробностей фильмов"""

    def get(self, request, pk):
        movie = Movie.objects.get(id=pk, draft=False)
        serializer = MovieDetailSerializer(movie)
        return Response(serializer.data)


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


from django.contrib.auth import get_user_model
