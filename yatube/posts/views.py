from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .forms import PostForm
from .models import Post, Group, User
from .utils import paginator_func


def index(request):
    """View функция для index."""
    post_list = Post.objects.all().order_by('-pub_date')
    context = {
        'page_obj': paginator_func(request, post_list),
    }

    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    """View функция для group_posts."""
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('group').order_by('-pub_date')
    context = {
        'group': group,
        'page_obj': paginator_func(request, post_list),
    }

    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    """View функция для profile."""
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('group').order_by('-pub_date')
    context = {
        'author': author,
        'page_obj': paginator_func(request, post_list),
    }

    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    """View функция для post_detail."""
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
    }

    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """View функция для создания записи."""
    form = PostForm(request.POST or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return redirect('posts:profile', post.author)

    return render(request, 'posts/create_post.html', {'form': form})


@login_required
def post_edit(request, post_id):
    """View функция для редактирования записи."""
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(request.POST or None, instance=post)
    if request.user != post.author:

        return redirect('posts:post_detail', post_id=post_id)

    if form.is_valid():
        form.save()

        return redirect('posts:post_detail', post_id=post_id)

    context = {
        'post_id': post_id,
        'form': form,
        'is_edit': True,
    }

    return render(request, 'posts/create_post.html', context)
