from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.generic.edit import CreateView

from .forms import RegisterForm
from .models import Channel


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

