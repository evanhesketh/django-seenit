import json

from django.http import (HttpResponseForbidden, HttpResponseNotFound,
                         JsonResponse)
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
from django.views.decorators.csrf import csrf_exempt

from .forms import RegisterForm, PostForm, CommentForm
from .models import User, Channel, Post, Comment


@login_required()
def home(request):
    return redirect(reverse('seenit:user_detail',
                            kwargs={"pk": request.user.id}))


def register_user(request):
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
    model = User

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        subscribed_channels = self.object.subscribed_channels.all()
        print("subscribed_channels=", subscribed_channels)
        context['channel_highlights'] = [channel.posts.all()[:2]
                                         for channel in subscribed_channels]
        print("context=", context)
        return context


class ChannelCreateView(CreateView):
    model = Channel
    fields = ["name"]
    template_name = 'seenit/channel_form.html'

    def get_success_url(self):
        return reverse('seenit:home')


class ChannelListView(ListView):
    template_name = 'seenit/channel_list.html'
    context_object_name = 'channel_list'

    def get_queryset(self):
        return Channel.objects.all()


class ChannelDetailView(DetailView):
    model = Channel

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['channel_id'] = self.kwargs['pk']
        context['form'] = PostForm()
        user_subscribed = self.object.determine_if_user_subscribed(
            self.request.user)
        print("user_subscribed=", user_subscribed)
        context['user_subscribed'] = user_subscribed
        return context


class ChannelDetailFormView(SingleObjectMixin, FormView):
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
        return reverse("seenit:channel-detail", kwargs={"pk": self.object.pk})


class ChannelView(View):
    def get(self, request, *args, **kwargs):
        view = ChannelDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ChannelDetailFormView.as_view()
        return view(request, *args, **kwargs)


class PostDetailView(DetailView):
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
        return reverse("seenit:post-detail",
                       kwargs={"pk": self.object.pk,
                               "channel_id": self.kwargs['channel_id']
                               }
                       )


class PostView(View):
    def get(self, request, *args, **kwargs):
        view = PostDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = PostDetailFormView.as_view()
        return view(request, *args, **kwargs)


def handle_reply(request, *args, **kwargs):
    text = request.POST.get('text')
    user = User.objects.get(pk=request.user.pk)
    post = Post.objects.get(pk=kwargs['post_id'])
    parent = Comment.objects.get(pk=kwargs['pk'])
    reply = Comment(text=text, user=user, post=post, parent=parent)
    reply.save()

    return HttpResponseRedirect(
        reverse("seenit:post-detail",
                kwargs={"pk": kwargs['post_id'],
                        "channel_id": kwargs['channel_id']
                        }
                ))


@csrf_exempt
def upvote(request):
    if request.method == "POST":
        body = json.loads(request.body)
        id = body['id']
        type = body['type']

        if type == "post":
            post = Post.objects.get(pk=id)
            post.rating += 1
            post.save()

        elif type == "comment":
            comment = Comment.objects.get(pk=id)
            comment.rating += 1
            comment.save()
        return JsonResponse({"updated": id, "type": type})
    return HttpResponseForbidden()


@csrf_exempt
def downvote(request):
    if request.method == "POST":
        body = json.loads(request.body)
        id = body['id']
        type = body['type']

        if type == "post":
            post = Post.objects.get(pk=id)
            post.rating -= 1
            post.save()

        elif type == "comment":
            comment = Comment.objects.get(pk=id)
            comment.rating -= 1
            comment.save()
        return JsonResponse({"updated": id, "type": type})
    return HttpResponseForbidden()


def subscribe(request, **kwargs):
    if request.method == "POST":
        channel_id = kwargs['channel_id']
        user_id = kwargs['user_id']
        user = get_object_or_404(User, pk=user_id)
        channel = get_object_or_404(Channel, pk=channel_id)
        user.subscribed_channels.add(channel)
        return HttpResponseRedirect(reverse("seenit:channel-detail",
                                            kwargs={"pk": channel_id}))
    return HttpResponseForbidden()


def unsubscribe(request, **kwargs):
    if request.method == "POST":
        channel_id = kwargs['channel_id']
        user_id = kwargs['user_id']
        user = get_object_or_404(User, pk=user_id)
        channel = get_object_or_404(Channel, pk=channel_id)
        user.subscribed_channels.remove(channel)
        return HttpResponseRedirect(reverse("seenit:channel-detail",
                                            kwargs={"pk": channel_id}))
    return HttpResponseForbidden()
