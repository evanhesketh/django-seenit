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
    path("channels/<int:channel_id>/posts/<int:pk>",
         views.PostView.as_view(), name="post-detail"),
    path("channels/<int:channel_id>/posts/<int:post_id>/comment/<int:pk>",
         views.handle_reply, name="reply"),
    path("api/v1/upvote", views.upvote, name="upvote"),
    path("api/v1/downvote", views.downvote, name="downvote"),
]
