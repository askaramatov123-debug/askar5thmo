python
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate

from .models import Category, Product, Review

User = get_user_model()



class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={'input_type': 'password'}
    )

    phone_number = serializers.RegexField(
        regex=r'^996\d{9}$',
        required=False,
        allow_null=True,
        allow_blank=True,
        error_messages={
            'invalid': (
                'Номер телефона должен начинаться с 996 '
                'и содержать 12 цифр. Например: 996555123456.'
            )
        }
    )

    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'phone_number']
        read_only_fields = ['id']

    def create(self, validated_data):
        password = validated_data.pop('password')

        return User.objects.create_user(
            email=validated_data.pop('email'),
            password=password,
            **validated_data
        )

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(
            request=self.context.get('request'),
            email=email,
            password=password
        )

        if user is None:
            raise ValidationError(
                'Неверный email или пароль.'
            )

        if not user.is_active:
            raise ValidationError(
                'Этот аккаунт неактивен.'
            )

        attrs['user'] = user
        return attrs

class CategorySerializer(serializers.ModelSerializer):
    products_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'products_count']

    def get_products_count(self, category):
        return Product.objects.filter(category=category).count()

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class ProductWithReviewsSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = [
            'id',
            'title',
            'description',
            'price',
            'category',
            'reviews',
            'rating'
        ]
        depth = 1
    def get_rating(self, obj):
        reviews = obj.reviews.all()

        if reviews.exists():
            return round(
                sum(review.stars for review in reviews) / reviews.count(),
                2
            )

        return None

class CategoryValidateSerializer(serializers.Serializer):
    name = serializers.CharField()