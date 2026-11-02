from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.core.validators import RegexValidator


phone_validator = RegexValidator(
    regex=r'^996\d{9}$',
    message='Номер телефона должен начинаться с 996 и содержать 12 цифр.'
)

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен для регистрации.')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user
    def create_superuser(self, email, password=None, **extra_fields):
        phone_number = extra_fields.get('phone_number')

        if not phone_number:
            raise ValueError('Для суперпользователя обязателен номер телефона.')

        phone_validator(phone_number)

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError(
                'Суперпользователь должен иметь is_superuser=True.'
            )

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True)

    phone_number = models.CharField(
        max_length=12,
        validators=[phone_validator],
        blank=True,
        null=True,
        verbose_name='Номер телефона'
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Category(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

class Product(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE
    )
    def __str__(self):
        return self.title
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'

STARS = (
    (i, "⭐" * i) for i in range(1, 6)
)

class Review(models.Model):
    text = models.TextField(null=True, blank=True)

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='reviews'
    )

    stars = models