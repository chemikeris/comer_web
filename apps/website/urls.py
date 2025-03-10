from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('help/', views.help, name='help'),
    path('api_help/', views.api_help, name='api_help'),
    path('tutorial/', views.tutorial, name='tutorial'),
    path('about/', views.about, name="about"),
    path('gtalign/help', views.gtalign_help, name='gtalign_help'),
    path('gtalign/tutorial', views.gtalign_tutorial, name='gtalign_tutorial'),
    path('gtalign/about', views.gtalign_about, name='gtalign_about'),
    path('gtalign/api', views.gtalign_api, name='gtalign_api'),
]
