from django.urls import path
from .views import *

urlpatterns = [
    # Página principal
    path('', IndexView.as_view(), name='index'),
    path('admin/', sitio_admin, name='sitio_admin'),
]