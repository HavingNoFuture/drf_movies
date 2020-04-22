from rest_framework import serializers

from .models import Movie, Review, Rating, Person, Country


class CountryListSerializer(serializers.ModelSerializer):
    """Вывод страны"""

    class Meta:
        model = Country
        fields = ('name', )


class PersonListSerializer(serializers.ModelSerializer):
    """Описание актера и режиссера"""

    class Meta:
        model = Person
        fields = ('id', 'first_name', 'last_name', 'image')


class PersonDetailSerializer(serializers.ModelSerializer):
    """Описание актера и режиссера"""
    countries = CountryListSerializer(read_only=True, many=True)

    class Meta:
        model = Person
        fields = '__all__'


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Добавлене отзыва."""

    class Meta:
        model = Review
        fields = "__all__"


class RecursiveSerializer(serializers.Serializer):
    """Рекурсивный вывод дочерних отзывов."""

    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class FilterReviewListSerializer(serializers.ListSerializer):
    """Фильтрует отзывы. Оставляет только родительские."""

    def to_representation(self, data):
        data = data.filter(parent=None)
        return super().to_representation(data)


class ReviewSerializer(serializers.ModelSerializer):
    """Вывод отзыва."""
    children = RecursiveSerializer(many=True)

    class Meta:
        list_serializer_class = FilterReviewListSerializer
        model = Review
        fields = ("name", "text", "children")


class RatingCreateSerializer(serializers.ModelSerializer):
    """Добавление рейтинга пользователем."""

    class Meta:
        model = Rating
        fields = ("star", "movie")

    def create(self, validated_data):
        rating = Rating.objects.update_or_create(
            ip=validated_data.get("ip", None),
            movie=validated_data.get("movie", None),
            defaults={"star": validated_data.get("star", None)}
        )
        return rating


class MovieListSerializer(serializers.ModelSerializer):
    """Список фильмов"""
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    rating_user = serializers.BooleanField()
    average_rating = serializers.FloatField()

    class Meta:
        model = Movie
        fields = ("id", "title", "tagline", "category", "rating_user", "average_rating")


class MovieDetailSerializer(serializers.ModelSerializer):
    """Подробности фильма"""
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    directors = PersonListSerializer(read_only=True, many=True)
    actors = PersonListSerializer(read_only=True, many=True)
    genres = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    countries = CountryListSerializer(many=True)
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = Movie
        exclude = ("draft",)
