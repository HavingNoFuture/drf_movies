from django.urls import path, include

from .yasg import urlpatterns as doc_urls
from . import views

urlpatterns = [
    path('movies/', views.MovieListView.as_view()),
    path('movies/<int:pk>', views.MovieDetailView.as_view()),
    path('review/', views.ReviewCreateView.as_view()),
    path('rating/', views.RatingCreateView.as_view()),
    path('persons/', views.PersonListView.as_view()),
    path('persons/<int:pk>', views.PersonDetailView.as_view()),
    path('api-auth/', include('rest_framework.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns += doc_urls


