from django.urls import path

from . import views
from chat.urls import urlpatterns

app_name = 'core'


urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
]