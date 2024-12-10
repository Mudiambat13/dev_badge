from django.contrib import admin
from .models import TechStack, DeveloperProfile

@admin.register(TechStack)
class TechStackAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(DeveloperProfile)
class DeveloperProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'linkedin_url', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('badge_uuid', 'created_at', 'updated_at')
