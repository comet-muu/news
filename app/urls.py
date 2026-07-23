from django.urls import path

from . import views

urlpatterns = [

    path(
        "",
        views.home,
        name="home"
    ),

    path(
        "mypage/",
        views.mypage,
        name="mypage"
    ),

    path(
        "blog/",
        views.blog,
        name="blog"
    ),

    path(
        "blog-settings/",
        views.blog_settings,
        name="blog_settings"
    ),

]
