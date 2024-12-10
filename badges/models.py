from django.db import models
from django.contrib.auth.models import User
import uuid

class TechStack(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(
        max_length=50,
        choices=[
            ('FRONTEND', 'Front-end'),
            ('BACKEND', 'Back-end'),
            ('LANGUAGE', 'Langage'),
            ('DATA', 'Data Science'),
            ('TOOLS', 'Outils'),
        ]
    )
    icon = models.ImageField(upload_to='tech_icons/')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['category', 'order', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class DeveloperProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        null=True,
        blank=True,
        default='profile_pics/default.png'
    )
    job_title = models.CharField(max_length=100, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=100, blank=True)
    linkedin_url = models.URLField(blank=True)
    github_url = models.URLField(blank=True)
    tech_stack = models.ManyToManyField('TechStack', blank=True)
    badge_uuid = models.UUIDField(unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profil de {self.user.username}"

    def get_profile_picture_url(self):
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return '/static/images/default-avatar.png'
