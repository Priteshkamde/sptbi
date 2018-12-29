from django.urls import path
from . import views


app_name = 'hire'

urlpatterns = [
    path('login/', views.login_user, name='login_user'),
    path('register/', views.register_user, name='register_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('post/', views.post_job, name='post_job'),
    path('', views.index, name='index'),
]
