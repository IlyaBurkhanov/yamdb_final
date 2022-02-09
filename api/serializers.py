from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from reviews.models import Categories, Comment, Genres, Review, Title

User = get_user_model()


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, username):
        if username != 'me':
            return username
        raise serializers.ValidationError(
            'У вас не может быть username "me"(')


class ObtainTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')
        read_only_fields = ['username']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    confirmation_code = serializers.CharField(source='password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['password']

    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        del data['refresh']
        data['access'] = str(refresh.access_token)
        return data

    class Meta:
        fields = ['username', 'confirmation_code']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genres
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category')


class ReadTitlesSerializer(TitleSerializer):
    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category')


class ActionTitlesSerializer(TitleSerializer):
    genre = SlugRelatedField(slug_field='slug',
                             queryset=Genres.objects.all(), many=True)
    category = SlugRelatedField(slug_field='slug',
                                queryset=Categories.objects.all())


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Review
        fields = ['id', 'text', 'author', 'score', 'pub_date']

    def validate(self, data):
        if self.context['request'].method != 'POST':
            return data
        user = self.context['request'].user
        title_id = self.context['view'].kwargs['title_id']
        title = get_object_or_404(Title, pk=title_id)

        if Review.objects.filter(
                title=title,
                author=user
        ).exists():
            raise serializers.ValidationError('Вы уже оставили оценку')
        return data


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'text', 'author', 'pub_date']
