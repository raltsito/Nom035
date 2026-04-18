from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'rol', 'tenant', 'is_active')
    list_filter = ('rol', 'is_active', 'tenant')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)

    fieldsets = UserAdmin.fieldsets + (
        ('Intra NOM-035', {'fields': ('rol', 'tenant')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Intra NOM-035', {'fields': ('email', 'rol', 'tenant')}),
    )
