from django.urls import path
from . import views

urlpatterns = [
    path('refresh', views.refresh_countries, name='refresh_countries'),
    path('', views.list_countries, name='list_countries'),
    path('image', views.get_summary_image, name='get_summary_image'),
    path('<str:name>', views.get_country, name='get_country'),
]

# Separate URL for delete to avoid conflicts
delete_urlpatterns = [
    path('<str:name>', views.delete_country, name='delete_country'),
]
