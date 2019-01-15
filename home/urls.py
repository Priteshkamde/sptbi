from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index, name='index'),
    path('change_password/', views.change_password, name='change_password'),
]
