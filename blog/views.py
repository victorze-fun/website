from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from .forms import EmailPostForm
from .models import Post


def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}\'s comments: {cd['comments']}"
            )
            send_mail(subject, message, 'your_account@gmail.com', [cd['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(
        request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent}
    )


class PostListView(ListView):
    # passes the page requested in a variable called page_obj
    # (model = Post) default -> query = Post.objects.all()
    queryset = Post.published.all()
    context_object_name = 'posts'  # default: object_list
    paginate_by = 3
    template_name = 'blog/post/list.html'  # default: blog/post_list


def post_list(request):
    post_list = Post.published.all()
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)  # ?page=3 (default 1)

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # If page_number is not an integer deliver the first page
        posts = paginator.page(1)
    except EmptyPage:
        # If page_number is out of range deliver last page of results
        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog/post/list.html', {'posts': posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish__year=year,
        publish__month=month,
        publish__day=day,
    )
    return render(request, 'blog/post/detail.html', {'post': post})
