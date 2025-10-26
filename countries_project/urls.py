"""
URL configuration for countries_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from app_countries import urls as countries_urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('countries/', include(countries_urls)),
    path('status', include([
        path('', include('app_countries.urls')),
    ])),
]

# Add delete endpoint separately
from app_countries.views import delete_country
urlpatterns += [
    path('app_countries/<str:name>', delete_country, name='delete_country_endpoint'),
]
