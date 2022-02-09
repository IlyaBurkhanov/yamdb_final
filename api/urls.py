from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoriesViewSet, CommentViewSet, CreateUserViewSet,
                    GenresViewSet, MyTokenObtainPairView, ReviewViewSet,
                    TitlesViewSet, UserViewSet)

app_name = 'api'

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('auth/signup', CreateUserViewSet, basename='create_users')
router.register('auth/token', MyTokenObtainPairView, basename='token')

router.register('categories', CategoriesViewSet, basename='Category')

router.register('genres', GenresViewSet, basename='Genres')
router.register('titles', TitlesViewSet, basename='Titles')

router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet, basename='reviews')

router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet, basename='comments')


urlpatterns = [
    path('v1/', include(router.urls)),
]
