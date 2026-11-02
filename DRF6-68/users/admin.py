from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import CustomUser


# Register your models here.
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ["id", "email", "is_active"]
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("is_active", "hands", "is_staff")}),
    )
