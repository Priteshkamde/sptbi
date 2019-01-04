from django.urls import path
from django.conf.urls import url
from . import views

app_name = 'hire'

urlpatterns = [
    path('login/', views.login_user, name='login_user'),
    path('register/', views.register_user, name='register_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('post/', views.post_job, name='post_job'),
    path('verify/<int:pk>/<slug:slug>', views.verify_email, name='verify'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('', views.index, name='index'),
]
