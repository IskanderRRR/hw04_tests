from django.conf import settings as conf_settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User

POSTS_PER_PAGE = conf_settings.POSTS_PER_PAGE


def index(request):
    template = "posts/index.html"
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "title": "Главная страница проекта YaTube",
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.all()
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "group": group,
        "page_obj": page_obj,
    }
    return render(request, "posts/group_list.html", context)


def profile(request, username):
    template = "posts/profile.html"
    author = User.objects.get(username=username)
    post_list = Post.objects.filter(author=author)
    paginator = Paginator(post_list, POSTS_PER_PAGE)
    post_count = post_list.count()
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {
        "page_obj": page_obj,
        "title": f"Профайл пользователя {username}",
        "author": author,
        "post_count": post_count,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = "posts/post_detail.html"
    post = Post.objects.get(id=post_id)
    group = post.group
    title = post.text[0:29]
    post_count = Post.objects.filter(author=post.author).count()
    context = {
        "post": post,
        "title": f"Пост {title}",
        "group": group,
        "post_count": post_count,
        "username": request.user.username,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    form = PostForm(request.POST or None)
    if form.is_valid():
        new_post = form.save(commit=False)
        new_post.author_id = request.user.id
        new_post.save()
        return redirect(f"/profile/{request.user.username}/")

    template = "posts/create_post.html"
    context = {
        "form": form,
    }

    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = Post.objects.get(pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect(f"/posts/{post_id}/")

    template = "posts/create_post.html"
    context = {
        "form": form,
        "is_edit": True,
    }

    return render(request, template, context)
