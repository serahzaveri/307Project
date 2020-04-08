from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.staticfiles.views import serve
from django.views.decorators.cache import cache_control

urlpatterns = [
	path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('', views.info, name='acc_info'),
    path('signup', views.signup, name='signup'),
    path('about', views.about, name='about'),
    path('login', views.do_login, name='login'),
    path('logout', views.do_logout, name='logout'),
    path('buy', views.buy, name='buy'),
]

#this code will allow for updates to static files to be viewed immediately by reloading the page

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, view=cache_control(no_cache=True, must_revalidate=True)(serve))
