from django.urls import path
from django.contrib.auth.decorators import login_required


from . import views

app_name = "seenit"

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_user, name="register"),
    path("users/<int:pk>/", login_required(views.UserDetailView.as_view()),
         name="user_detail"),
    path("create_channel/",
         login_required(views.create_channel),
         name="create_channel"),
    path("channels/", login_required(
        views.ChannelListView.as_view()), name="channels"),
    path("channels/<int:pk>/",
         login_required(views.ChannelView.as_view()), name="channel_detail"),
    path("channels/<int:channel_id>/posts/<int:pk>/",
         login_required(views.PostView.as_view()), name="post_detail"),
    path("channels/<int:channel_id>/posts/<int:post_id>/comment/<int:pk>/",
         views.handle_reply, name="reply"),
    path("<str:post_type>/<int:pk>/upvote/", views.upvote, name="upvote"),
    path("<str:post_type>/<int:pk>/downvote/", views.downvote,
         name="downvote"),
    path("users/<int:user_id>/channels/<int:channel_id>/subscribe/",
         views.subscribe, name="subscribe"),
    path("users/<int:user_id>/channels/<int:channel_id>/unsubscribe/",
         views.unsubscribe, name="unsubscribe"),
]
