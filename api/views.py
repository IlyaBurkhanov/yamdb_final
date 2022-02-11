from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.db.models import Avg
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Categories, Genres, Review, Title

from .filters import CustomSearchFilter
from .permissions import (AdminOnly, GenresCategoriesPermission,
                          IsOwnerAdminModeratorOrReadOnly)
from .serializers import (ActionTitlesSerializer, CategorySerializer,
                          CommentSerializer, CreateUserSerializer,
                          GenreSerializer, ObtainTokenSerializer,
                          ReadTitlesSerializer, ReviewSerializer,
                          UserSerializer)

User = get_user_model()


def send_code(user, code):
    subject = 'Ваш код подтверждения'
    message = f'{code} - код для входа'
    email = [user.email]
    return send_mail(subject, message, settings.DJANGO_EMAIL, email)


class CreateUserViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    serializer_class = CreateUserSerializer
    permission_classes = [AllowAny, ]

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(
                data=serializer.data,
                status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        code = PasswordResetTokenGenerator().make_token(user)
        send_code(user, code)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class MyTokenObtainPairView(viewsets.ViewSet):
    queryset = User.objects.all()
    serializer_class = ObtainTokenSerializer
    permission_classes = [AllowAny, ]

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if 'username' not in request.data:
            return Response({'Отсутствует обязательное поле "username"'},
                            status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid(raise_exception=True):
            username = request.data['username']
            user = get_object_or_404(User, username=username)
            if PasswordResetTokenGenerator().check_token(
                    user, request.data['confirmation_code']):
                token = RefreshToken.for_user(user)
                return Response(
                    {'token': str(token.access_token)},
                    status=status.HTTP_200_OK
                )
        return Response({'Проверьте правильность введённого кода'},
                        status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    lookup_field = 'username'
    permission_classes = [IsAuthenticated, AdminOnly]

    @action(
        detail=False,
        methods=['get', 'patch'],
        url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def about_me(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        if request.method == 'GET':
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(email=user.email, role=user.role)
        return Response(serializer.data, status=status.HTTP_200_OK)


ClassGenreCategory = type(
    'ClassGenreCategory',

    (mixins.ListModelMixin,
     mixins.CreateModelMixin,
     mixins.DestroyModelMixin,
     viewsets.GenericViewSet),

    {'pagination_class': PageNumberPagination,
     'permission_classes': (GenresCategoriesPermission,),
     'filter_backends': (filters.SearchFilter,),
     'search_fields': ('name', 'slug'),
     'lookup_field': 'slug'
     }
)


class GenreCategoryViewSet(ClassGenreCategory):
    pagination_class = PageNumberPagination
    permission_classes = (GenresCategoriesPermission,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', 'slug')
    lookup_field = 'slug'


class CategoriesViewSet(mixins.RetrieveModelMixin,
                        mixins.UpdateModelMixin,
                        ClassGenreCategory):
    queryset = Categories.objects.all()
    serializer_class = CategorySerializer


class GenresViewSet(GenreCategoryViewSet):
    queryset = Genres.objects.all()
    serializer_class = GenreSerializer


class TitlesViewSet(viewsets.ModelViewSet):
    pagination_class = PageNumberPagination
    permission_classes = (GenresCategoriesPermission,)
    filter_backends = (CustomSearchFilter,)
    queryset = Title.objects.annotate(
        rating=Avg('title_reviews__score')).order_by('-id')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return ReadTitlesSerializer
        return ActionTitlesSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = [IsOwnerAdminModeratorOrReadOnly]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        return title.title_reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs['title_id'])
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsOwnerAdminModeratorOrReadOnly]

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            pk=self.kwargs['review_id'],
            title__id=self.kwargs['title_id'])
        return review.review_comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs['review_id'],
            title__id=self.kwargs['title_id'])
        serializer.save(author=self.request.user, review=review)


def index_v2(request):
    return HttpResponse("Для api2! В разработке!")
