from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .yasg import urlpatterns as doc_urls
from . import views


router = DefaultRouter()
router.register('movies', views.MovieViewSet)
router.register('persons', views.PersonViewSet)
router.register('reviews', views.ReviewViewSet)
router.register('ratings', views.RatingViewSet)


urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

urlpatterns += router.urls
urlpatterns += doc_urls




