from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('help/', views.help, name='help'),
    path('api_help/', views.api_help, name='api_help'),
    path('tutorial/', views.tutorial, name='tutorial'),
    path('about/', views.about, name="about"),
]
