from django.urls import path


from . import views

app_name = "seenit"

urlpatterns = [
    path("", views.home, name="home"),
    path("register", views.register_user, name="register"),
    path("create_channel",
         views.ChannelCreateView.as_view(),
         name="create_channel"),
    path("channels", views.ChannelListView.as_view(), name="channels"),
    path("channels/<int:pk>",
         views.ChannelView.as_view(), name="channel-detail"),
#     path("channels/<int:channel_id>/new_post",
#          views.PostCreateView.as_view(),
#          name="new_post"),
]
