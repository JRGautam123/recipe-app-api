from django.contrib import admin
from core import models
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin


class UserAdmin(BaseUserAdmin):
    """Define the admin page for users."""
    # for admin main page
    ordering = ['id']
    list_display = ['email', 'name']
    # for user change/update page
    fieldsets = [
        (
            None,
            {'fields': ['email', 'password']}
        ),

        (
            'Permission',
            {'fields': ['is_active', 'is_staff', 'is_superuser']}
        ),

        (
            'Last Login',
            {'fields': ['last_login']}
        )
    ]
    readonly_fields = ['last_login']
    # for add user page
    add_fieldsets = [
        (
            None,
            {
                'classes': ['wide'],
                'fields': [
                    'email', 'password', 'name',
                    'is_active', 'is_staff', 'is_superuser'
                ]
            }
        )
    ]


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)
