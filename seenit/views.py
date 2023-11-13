from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.views import View
from django.views.generic.edit import CreateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic import ListView, DetailView, FormView

from .forms import RegisterForm, PostForm
from .models import User, Channel, Post


def home(request):
    return render(request, 'seenit/home.html', {})


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
                    user_id=user, channel_id=self.object)
        post.save()
        return super().form_valid(form)

    def get_success_url(self):
        print("pk=", self.object.pk)
        return reverse("seenit:channel-detail", kwargs={"pk": self.object.pk})


class ChannelView(View):
    def get(self, request, *args, **kwargs):
        print("kwargs=", kwargs)
        view = ChannelDetailView.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = ChannelDetailFormView.as_view()
        return view(request, *args, **kwargs)
