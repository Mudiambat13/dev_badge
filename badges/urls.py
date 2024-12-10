from django.urls import path
from . import views

app_name = 'badges'


urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('badge/', views.generate_badge, name='generate_badge'),
    path('card/', views.generate_dev_card, name='generate_pdf'),
]