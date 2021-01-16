from django.conf.urls import url
from .views import *

from django.urls import path, include

from rest_framework.routers import DefaultRouter


urlpatterns = [
    url(
        r'^api/v1/bookmarks/?$',
        bookmarks,
        name='bookmarks'
    ),
    url(
        r'^api/v1/bookmarks/(?P<id>[0-9]+)$',
        delete_bookmark,
        name='delete_bookmark'
    ),
    url(
        r'^api/v1/posts/?$',
        get_add_posts,
        name='get_add_posts'
    ),
    url(
        r'^api/v1/upload/?$',
        upload_file,
        name='upload_file'
    ),
    url(
        r'^api/v1/login/?$',
        login,
        name='login'
    ),
    url(r'^api/v1/signup', SignUPView.as_view(), name="signup"),
    url(r'^api/v1/social/(?P<type>\w+)/?$',SocialLoginView.as_view(),name='social_signup'),
    url(r'^api/v1/post/(?P<id>[0-9]+)/comment', CommentView.as_view(), name="add_comment"),
    url(r'^api/v1/comment/(?P<pk>[0-9]+)/?$', CommentView.as_view(), name="delete_comment"),
    url(r'^api/v1/post/(?P<id>[0-9]+)/hide',HidePostView.as_view(),name='hide_post'),
    url(r'^api/v1/post/(?P<id>[0-9]+)/share',SharePostView.as_view(),name='share_post'),
    url(r'^api/v1/post/(?P<id>[0-9]+)/report',ReportPostView.as_view(),name='report_post'),
    url(r'^api/v1/post/(?P<id>[0-9]+)/(?P<action>\w+)/?$', userPostInteraction.as_view(), name="post_interaction"),
    url(r'^api/v1/posts/(?P<id>[0-9]+)/?$', PostView.as_view(), name="post"),
    url(r'^api/v1/user/(?P<pk>[0-9]+)/setting', userPereference.as_view(), name="preference"),
    url(r'^api/v1/user/(?P<pk>[0-9]+)/feed/(?P<type>\w+)/?$', userFeeds.as_view(), name="user_feed"),
    url(r'^api/v1/change_password', ChangePasswordView.as_view(), name="change_password"),
    url(r'^api/v1/user/(?P<id>[0-9]+)/?$', UserView.as_view(), name="update_user"),
    url(r'^api/v1/comment/(?P<id>[0-9]+)/report',ReportComment.as_view(),name='report_comment'),
    url(r'^api/v1/notifications',GetAllNotifications.as_view(),name='notifications'),
    url(r'^api/v1/users/(?P<id>[0-9]+)',UserView.as_view(),name='get_user'),
    url(r'^api/v1/admin',AdminLogin.as_view(),name='add_admin'),
    url(r'^api/v1/users',AdminUserView.as_view(),name='get_users'),
    url(r'^api/v1/user-status/(?P<id>[0-9]+)',AdminUserView.as_view(),name='user_status'),
    url(r'^api/v1/delete_post/(?P<id>[0-9]+)',DeletePost.as_view(),name='delete_post'),
    url(r'^api/v1/add_admin',AddAdmin.as_view(),name='add_admin'),
    url(r'^api/v1/reported-posts',ReportedPosts.as_view(),name='reported-posts'),
    url(r'^api/v1/user/country', UserCountryView.as_view(), name="user_countries"),
    url(r'^api/v1/reset_password', ResetPassword.as_view(), name="reset_password")
]