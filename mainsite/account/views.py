from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.contrib.auth.models import User, auth
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from . import forms
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from account.models import ItemPost #really should be in item, same with line below
from account.forms import CreateItemPostForm, UpdateItemPostForm
from django.shortcuts import render
from operator import attrgetter
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from account.models import ItemPost
from django.views.generic import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

# Create your views here.

@login_required
def info(request):
    return HttpResponse('Hello ' + request.user.username)

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def buy(request):
    return render(request, 'buy.html')

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
    logout(request)
    return HttpResponseRedirect(reverse('login'))

def create_item_view(request):

    context = {}

    user = request.user
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    form = CreateItemPostForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        obj = form.save(commit=False)
        author = User.objects.filter(email=user.email).first()
        obj.author = author
        obj.save()
        form = CreateItemPostForm()

    context['form'] = form

    return render(request, 'create_item.html', context)


def detail_item_view(request, slug):

    context = {}

    item_post = get_object_or_404(ItemPost, slug=slug)
    context['item_post'] = item_post

    return render(request, 'detail_item.html', context)



def edit_item_view(request, slug):

    context = {}

    user = request.user
    if not user.is_authenticated:
        return redirect("must_authenticate")

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


item_POSTS_PER_PAGE = 9

def home_screen_view(request, *args, **kwargs):
    
    context = {}

    # Search
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

class PostDelete(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ItemPost
    success_url = reverse_lazy('home2')
    login_url = reverse_lazy('login')

    def test_func(self):
        return ItemPost.objects.get(id=self.kwargs['pk']).author == self.request.user