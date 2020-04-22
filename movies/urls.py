from django.urls import path

from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('movies/', views.MovieListView.as_view()),
    path('movies/<int:pk>', views.MovieDetailView.as_view()),
    path('review/', views.ReviewCreateView.as_view()),
    path('rating/', views.RatingCreateView.as_view()),
    path('openapi', get_schema_view(
        title="drf movies",
        description="API for all things …",
        version="1.0.0"
    ), name='openapi-schema'),
    path('swagger-ui/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),
]
