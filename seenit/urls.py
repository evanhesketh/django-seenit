from django.urls import path


from . import views

app_name = "seenit"

urlpatterns = [
    path("", views.home, name="home"),
    path("register", views.register_user, name="register"),
    path("create_channel",
         views.ChannelCreateView.as_view(),
         name="create_channel")
]
