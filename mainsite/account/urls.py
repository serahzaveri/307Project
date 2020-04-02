from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.home),
    path('signup', views.signup, name='signup'),
]