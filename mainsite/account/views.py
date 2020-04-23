from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from . import forms
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from account.models import ItemPost, Order, Cart, Checkout
from account.forms import CreateItemPostForm, UpdateItemPostForm, OrderCreateForm
from django.shortcuts import render
from operator import attrgetter
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.views.generic import CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Create your views here.

@login_required
def info(request):
    return HttpResponse('Hello ' + request.user.username)

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def buy(request):
    #seems to have fixed the problem when same procedure as home_screen is used
    
    context = {}

    # get and display all item posts
    query = ""
    if request.GET:
        query = request.GET.get('q', '')
        context['query'] = str(query)

    item_posts = sorted(get_item_queryset(query), key=attrgetter('date_updated'), reverse=True)
    
    # Pagination
    page = request.GET.get('page', 1)
    item_posts_paginator = Paginator(item_posts, item_POSTS_PER_PAGE)
    try:
        item_posts = item_posts_paginator.page(page)
    except PageNotAnInteger:
        item_posts = item_posts_paginator.page(item_POSTS_PER_PAGE)
    except EmptyPage:
        item_posts = item_posts_paginator.page(item_posts_paginator.num_pages)

    context['item_posts'] = item_posts

    return render(request, "buy.html", context)

def signup(request):
    context = {}
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            try:
              user = User.objects.create_user(
                form.cleaned_data['username'], 
                email=form.cleaned_data['email'], 
                password=form.cleaned_data['password'])
              return HttpResponseRedirect(reverse('login'))
            except IntegrityError:
                form.add_error('username', 'Username is taken')

        context['form'] = form   
    return render(request, 'signup.html', context)

def do_login(request):
    context = {}
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(request, 
              username=form.cleaned_data['username'], 
              password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)
                if 'next' in request.GET:
                    return HttpResponseRedirect(request.GET['next'])
                return HttpResponseRedirect(reverse('acc_info'))
            else:
                form.add_error(None, 'Unable to log in')
        context['form'] = form
    return render(request, 'login.html', context)

def do_logout(request):
    if request.user.is_authenticated:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(request.user.username, {
            'type': 'logout_message',
            'message': 'Disconnecting. You logged out from another browser or tab.'})

    logout(request)
    return HttpResponseRedirect(reverse('login'))


#create an item post

def create_item_view(request):

    context = {}

    user = request.user
    if not user.is_authenticated:
        messages.warning(request, "You must login to view that page.")
        return redirect ("login")

    form = CreateItemPostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        obj = form.save(commit=False)
        author = User.objects.filter(email=user.email).first()
        obj.author = author
        obj.save()
        context['success_message'] = "Posted"
        form = CreateItemPostForm()

    context['form'] = form

    return render(request, 'create_item.html', context)

#detailed view for an item

def detail_item_view(request, slug):

    context = {}

    item_post = get_object_or_404(ItemPost, slug=slug)
    context['item_post'] = item_post

    return render(request, 'detail_item.html', context)

#view to edit item

def edit_item_view(request, slug):

    context = {}

    user = request.user
    if not user.is_authenticated:
        messages.warning(request, "You must login to view that page.")
        return redirect ("login")

    item_post = get_object_or_404(ItemPost, slug=slug)

    if item_post.author != user:
        return HttpResponse('You are not the author of that post.')

    if request.POST:
        form = UpdateItemPostForm(request.POST or None, request.FILES or None, instance=item_post)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            context['success_message'] = "Updated"
            item_post = obj

    form = UpdateItemPostForm(
            initial = {
                    "title": item_post.title,
                    "body": item_post.body,
                    "price": item_post.price,
                    "inventory": item_post.inventory,
                    "image": item_post.image,
            }
        )

    context['form'] = form
    return render(request, 'edit_item.html', context)

#search results view

class SearchResultsView(TemplateView):
    template_name = 'search_results.html'

    def get(self, request, *args, **kwargs):
        q = request.GET.get('q', '')
        self.results = ItemPost.objects.filter(Q(title__icontains=q) | Q(body__icontains=q)).distinct()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(results=self.results, **kwargs)

#item queryset to use for homs_screen_view, sorting posts

def get_item_queryset(query=None):
    queryset = []
    queries = query.split(" ") # python install 2019 = [python, install, 2019]
    for q in queries:
        posts = ItemPost.objects.filter(
                Q(title__icontains=q) | 
                Q(body__icontains=q)
            ).distinct()

        for post in posts:
            queryset.append(post)

    return list(set(queryset))  


item_POSTS_PER_PAGE = 2

#home screen view 

def home_screen_view(request, *args, **kwargs):
    
    context = {}

    # get and display all item posts
    query = ""
    if request.GET:
        query = request.GET.get('q', '')
        context['query'] = str(query)

    item_posts = sorted(get_item_queryset(query), key=attrgetter('date_updated'), reverse=True)
    
    # Pagination
    page = request.GET.get('page', 1)
    item_posts_paginator = Paginator(item_posts, item_POSTS_PER_PAGE)
    try:
        item_posts = item_posts_paginator.page(page)
    except PageNotAnInteger:
        item_posts = item_posts_paginator.page(item_POSTS_PER_PAGE)
    except EmptyPage:
        item_posts = item_posts_paginator.page(item_posts_paginator.num_pages)

    context['item_posts'] = item_posts

    return render(request, "home2.html", context)

#delete item post: user must be logged in 

class PostDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ItemPost
    success_url = reverse_lazy('home2')
    login_url = reverse_lazy('login')

    def test_func(self):
        return ItemPost.objects.get(id=self.kwargs['pk']).author == self.request.user

# Add to Cart View

def add_to_cart(request, slug):

    user = request.user

    if not user.is_authenticated:
        messages.warning(request, "You must login to view that page.")
        return redirect ("login")

    item = get_object_or_404(ItemPost, slug=slug)    
    order_item, created = Cart.objects.get_or_create(
        item=item,
        user=user,
        purchased=False
    )
    if item.inventory < 1:
        messages.info(request, "Out of stock!")
        return redirect("home2")
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.orderitems.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, f"{item.title} quantity was updated.")
            return redirect("home2")
        else:
            order.orderitems.add(order_item)
            messages.info(request, f"{item.title} was added to your cart.")
            return redirect("home2")
    else:
        order = Order.objects.create(
            user=request.user)
        order.orderitems.add(order_item)
        messages.info(request, f"{item.title} was added to your cart.")
        return redirect("home2")

# Remove entire quantity of an item from cart

def remove_from_cart(request, slug):
    item = get_object_or_404(ItemPost, slug=slug)
    cart_qs = Cart.objects.filter(user=request.user, item=item)
    if cart_qs.exists():
        cart = cart_qs[0]
        # Checking the cart quantity
        if cart.quantity > 0:
            cart_qs.delete()
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.orderitems.filter(item__slug=item.slug).exists():
            order_item = Cart.objects.filter(
                item=item,
                user=request.user,
            )[0]
            order.orderitems.remove(order_item)
            messages.warning(request, "This item was removed from your cart.")
            return redirect("cart")
        else:
            messages.warning(request, "This item was not in your cart")
            return redirect("cart")
    else:
        messages.warning(request, "You do not have an active order")
        return redirect("cart")


# Cart View
def CartView(request):

    user = request.user

    if not user.is_authenticated:
        messages.warning(request, "You must login to view that page.")
        return redirect ("login")

    carts = Cart.objects.filter(user=user, purchased=False)
    orders = Order.objects.filter(user=user, ordered=False)
    order = orders[0]

    if carts.exists():
        if orders.exists():
            order = orders[0]
    else:
        messages.warning(request, "Your cart is empty. You must add an item to your cart.")
        return redirect ("home2")
    
    context = {
        'carts': carts,
        'order': order,
    }

    return render (request, "cart.html", context)


# Decrease the quantity of the cart:

def decreaseCart(request, slug):
    item = get_object_or_404(ItemPost, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.orderitems.filter(item__slug=item.slug).exists():
            order_item = Cart.objects.filter(
                item=item,
                user=request.user
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.orderitems.remove(order_item)
                order_item.delete()
                messages.warning(request, f"{item.title} was removed from your cart.")
            messages.info(request, f"{item.title} quantity was updated.")
            return redirect("cart")
        else:
            messages.info(request, f"{item.title} quantity was updated.")
            return redirect("cart")
    else:
        messages.info(request, "You do not have an active order")
        return redirect("buy")

# checkout view

def checkout_create(request):
    user = request.user

    if not user.is_authenticated:
        messages.warning(request, "You must login to view that page.")
        return redirect ("login")

    carts = Cart.objects.filter(user=user, purchased=False)
    orders = Order.objects.filter(user=user, ordered=False)
    order = orders[0]

    if carts.exists():
        if orders.exists():
            order = orders[0]
    else:
        messages.warning(request, "Your cart is empty. You must add an item to your cart.")
        return redirect ("home2")

    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        checkout = form.save()
        for cart in carts:
            cart.item.inventory -= cart.quantity
            cart.item.save()
            cart.delete()
        return render(request, 'checkout_done.html', {'checkout': checkout})
    else:
        form = OrderCreateForm()
        return render(request, 'checkout.html', {'form': form, 'order': order, 'carts':carts})

#checkout done view

def checkout_done(request):
    return render(request, 'checkout_done.html')
