from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.home),
    path('', views.info, name='acc_info'),
    path('signup', views.signup, name='signup'),
    path('about', views.about, name='about'),
    path('login', views.do_login, name='login'),
    path('logout', views.do_logout, name='logout'),
]