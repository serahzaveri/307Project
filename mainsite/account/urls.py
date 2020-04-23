from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from . import views
from django.contrib.staticfiles.views import serve
from django.views.decorators.cache import cache_control
from account.views import (
	create_item_view,
	detail_item_view,
	edit_item_view,
	home_screen_view,
    PostDelete,
    decreaseCart,
    remove_from_cart,
    add_to_cart,
    CartView,
    checkout_create,
    checkout_done,
    SearchResultsView,
)



urlpatterns = [
    path('', home_screen_view, name='home2'),
    path('home2', home_screen_view, name='home2'),
    path('', views.info, name='acc_info'),
    path('signup', views.signup, name='signup'),
    path('about', views.about, name='about'),
    path('login', views.do_login, name='login'),
    path('logout', views.do_logout, name='logout'),
    path('buy', views.buy, name='buy'),
    path('cart', views.CartView, name='cart'),
    path('checkout', views.checkout_create, name='checkout'),
    path('checkout_done', views.checkout_done, name='checkout_done'),
    path('create', views.create_item_view, name="create"),
    path('search', SearchResultsView.as_view(), name="search"),
    path('<slug>', views.detail_item_view, name="detail"),
    path('<slug>/edit', views.edit_item_view, name="edit"),
    path('<int:pk>/delete', PostDelete.as_view(), name='delete'),
    path('cart/<slug>', views.add_to_cart, name='add-cart'),
    path('remove/<slug>', views.remove_from_cart, name='remove-cart'),
    path('cart/decrease/<slug>', views.decreaseCart, name='decrease-cart'),

]

#this code will allow for updates to static files to be viewed immediately by reloading the page

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, view=cache_control(no_cache=True, must_revalidate=True)(serve))