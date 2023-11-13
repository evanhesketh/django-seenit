from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import User, Post


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ["title", "text"]
