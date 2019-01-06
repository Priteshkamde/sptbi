from django.conf.urls import url
from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.decorators.cache import never_cache
from . import views


app_name = 'apply'

urlpatterns = [
    path('login/', never_cache(views.login_user), name='login_user'),
    path('register/', never_cache(views.register_user), name='register_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('detail/<int:pk>', views.detail, name='detail'),
    path('profile/<int:pk>', views.profile, name='profile'),
    path('verify/<int:pk>/<slug:slug>', views.verify_email, name='verify'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('', views.index, name='index'),
]
