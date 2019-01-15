from django.urls import path
from django.conf.urls import url
from django.views.decorators.cache import never_cache
from . import views

app_name = 'hire'

urlpatterns = [
    path('login/', never_cache(views.login_user), name='login_user'),
    path('register/', never_cache(views.register_user), name='register_user'),
    path('logout/', views.logout_user, name='logout_user'),
    path('post/', never_cache(views.post_job), name='post_job'),
    path('verify/<int:pk>/<slug:slug>/', views.verify_email, name='verify'),
    path('<int:app_id>/shortlist/', views.shortlist, name='shortlist'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('profile/edit/', never_cache(views.edit_profile), name='edit_profile'),
    path('post/<int:pk>/edit/', never_cache(views.edit_post), name='edit_post'),
    path('post/<int:pk>/delete/', never_cache(views.delete_post), name='delete_post'),
    path('', views.index, name='index'),
]
