"""comer_web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('', include('apps.website.urls')),
    path('search/', include('apps.search.urls')),
    path('model_structure/', include('apps.model_structure.urls')),
    #path('admin/', admin.site.urls),
    path('msa/', include('apps.msa.urls')),
    path('gtalign/', include('apps.structure_search.urls')),
    path('gtalign/superposition/', include('apps.superposition.urls')),
]
