from rest_framework import serializers

from .models import Movie, Review


class MovieListSerializer(serializers.ModelSerializer):
    """Список фильмов"""
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Movie
        fields = ("title", "tagline", "category")

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


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


class MovieDetailSerializer(serializers.ModelSerializer):
    """Подробности фильма"""
    category = serializers.SlugRelatedField(slug_field="name", read_only=True)
    directors = serializers.SlugRelatedField(slug_field="first_name", read_only=True, many=True)
    actors = serializers.SlugRelatedField(slug_field="first_name", read_only=True, many=True)
    genres = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    countries = serializers.SlugRelatedField(slug_field="name", read_only=True, many=True)
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = Movie
        exclude = ("draft", )
