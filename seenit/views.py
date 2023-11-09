from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic.edit import CreateView
from django.views.generic import ListView

from .forms import RegisterForm
from .models import Channel, Post, Comment


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


class PostCreateView(CreateView):
    model = Post
    fields = ["title", "text"]

    def form_valid(self, form):
        user_id = self.request.user.id
        channel_id = self.kwargs['channel_id']
        form.instance.channel_id = channel_id
        form.instance.user_id = user_id
        return super().form_valid(form)

    def get_success_url(self):
        channel_id = self.kwargs['channel_id']
        return reverse(f'seenit:channels/{channel_id}')
