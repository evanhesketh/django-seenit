from django.http import HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import (render, redirect, HttpResponseRedirect,
                              get_object_or_404)
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.views.generic.edit import CreateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import ListView, DetailView, FormView

from .forms import RegisterForm, PostForm, CommentForm
from .models import User, Channel, Post, Comment

###############################################################################
# Homepage


@login_required()
def home(request):
    """Logged-in: redirect to user detail page
    Logged-out: redirect to login page
    """

    return redirect(reverse('seenit:user_detail',
                            kwargs={"pk": request.user.id}))

###############################################################################
# User views


def register_user(request):
    """Handle user signup.
    If form valid, create new user, add to db and redirect to homepage
    Otherwise, present signup form
    """

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Registration Successful!")
            return redirect('/')
    else:
        form = RegisterForm()
    return render(request, 'seenit/auth/register.html', {'form': form})


class UserDetailView(DetailView):
    """Show user details page"""

    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subscribed_channels = self.object.subscribed_channels.all()
        context['channel_highlights'] = [channel.posts.all()[:2]
                                         for channel in subscribed_channels]
        context['top_posts'] = self.object.get_top_posts()
        return context

###############################################################################
# Channel views


class ChannelCreateView(CreateView):
    """Form for creating a new channel.
    If successful, redirect to homepage
    Otherwise, present form
    """

    model = Channel
    fields = ["name"]
    template_name = 'seenit/channel_form.html'

    def get_success_url(self):
        return reverse('seenit:home')


class ChannelListView(ListView):
    """Display a list of all channels"""

    template_name = 'seenit/channel_list.html'
    context_object_name = 'channel_list'

    def get_queryset(self):
        return Channel.objects.all()


class ChannelDetailView(DetailView):
    """Display a channel and associated posts"""

    model = Channel

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channel_id'] = self.kwargs['pk']
        context['form'] = PostForm()
        user_subscribed = self.object.determine_if_user_subscribed(
            self.request.user)

        context['user_subscribed'] = user_subscribed
        return context


class ChannelDetailFormView(SingleObjectMixin, FormView):
    """Handle adding a new post to a channel.
    If form is valid, create a new post and add to db
    Otherwise, present form
    """

    template_name = 'seenit/channel_detail.html'
    form_class = PostForm
    model = Channel

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        title = self.request.POST.get("title")
        text = self.request.POST.get("text")
        user = User.objects.get(pk=self.request.user.pk)
        post = Post(title=title, text=text,
                    user=user, channel=self.object)
        post.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("seenit:channel_detail", kwargs={"pk": self.object.pk})


class ChannelView(View):
    """Handle routing for GET and POST requests to channel detail view"""

    def get(self, request, *args, **kwargs):
        view = ChannelDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ChannelDetailFormView.as_view()
        return view(request, *args, **kwargs)


def subscribe(request, **kwargs):
    """Handle subscribing to a channel.
    Redirect to channel detail page
    """

    if request.method == "POST":
        channel_id = kwargs['channel_id']
        user_id = kwargs['user_id']
        user = get_object_or_404(User, pk=user_id)
        channel = get_object_or_404(Channel, pk=channel_id)
        user.subscribed_channels.add(channel)
        return HttpResponseRedirect(reverse("seenit:channel_detail",
                                            kwargs={"pk": channel_id}))
    return HttpResponseForbidden()


def unsubscribe(request, **kwargs):
    """Handle unsubscribing to a channel.
    Redirect to channel detail page
    """

    if request.method == "POST":
        channel_id = kwargs['channel_id']
        user_id = kwargs['user_id']
        user = get_object_or_404(User, pk=user_id)
        channel = get_object_or_404(Channel, pk=channel_id)
        user.subscribed_channels.remove(channel)
        return HttpResponseRedirect(reverse("seenit:channel_detail",
                                            kwargs={"pk": channel_id}))
    return HttpResponseForbidden()

###############################################################################
# Post/comment views


class PostDetailView(DetailView):
    """Display a post and associated comment threads"""

    model = Post

    def get(self, request, *args, **kwargs):
        channel = Channel.objects.get(pk=self.kwargs['channel_id'])
        if not channel.posts.filter(pk=self.kwargs['pk']):
            return HttpResponseNotFound()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        comments = Comment.objects.filter(post=self.object)
        for comment in comments:
            print(comment.parent)
        context['comments'] = Comment.objects.filter(post=self.object)
        context['post_id'] = self.kwargs['pk']
        context['form'] = CommentForm()
        return context


class PostDetailFormView(SingleObjectMixin, FormView):
    """Handle adding a new comment to a post
    If form is valid, create comment and add to db
    Otherwise, present form
    """

    template_name = 'seenit/post_detail.html'
    form_class = CommentForm
    model = Post

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        text = self.request.POST.get("text")
        user = User.objects.get(pk=self.request.user.pk)
        comment = Comment(text=text,
                          user=user, post=self.object)
        comment.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("seenit:post_detail",
                       kwargs={"pk": self.object.pk,
                               "channel_id": self.kwargs['channel_id']
                               }
                       )


class PostView(View):
    """Handle routing for GET and POST requests to post detail view"""

    def get(self, request, *args, **kwargs):
        view = PostDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = PostDetailFormView.as_view()
        return view(request, *args, **kwargs)


def handle_reply(request, *args, **kwargs):
    """Handle reply to a comment.
    Create reply and add to db
    """

    text = request.POST.get('text')
    user = User.objects.get(pk=request.user.pk)
    post = Post.objects.get(pk=kwargs['post_id'])
    parent = Comment.objects.get(pk=kwargs['pk'])
    reply = Comment(text=text, user=user, post=post, parent=parent)
    reply.save()

    return HttpResponseRedirect(
        reverse("seenit:post_detail",
                kwargs={"pk": kwargs['post_id'],
                        "channel_id": kwargs['channel_id']
                        }
                ))


def upvote(request, **kwargs):
    """Handle upvote for a post or comment.
    Redirect to same page
    """

    if request.method == "POST":
        id = kwargs['pk']
        type = kwargs['post_type']

        if type == "post":
            post = Post.objects.get(pk=id)
            post.upvote(request.user)

        elif type == "comment":
            comment = Comment.objects.get(pk=id)
            comment.upvote(request.user)

        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    return HttpResponseForbidden()


def downvote(request, **kwargs):
    """Handle downvote for a post or comment.
    Redirect to same page
    """

    if request.method == "POST":
        id = kwargs['pk']
        type = kwargs['post_type']

        if type == "post":
            post = Post.objects.get(pk=id)
            post.downvote(request.user)

        elif type == "comment":
            comment = Comment.objects.get(pk=id)
            comment.downvote(request.user)

        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    return HttpResponseForbidden()
