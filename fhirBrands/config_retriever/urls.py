# config_retriever/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.retrieve_config, name='retrieve_config'),
]
