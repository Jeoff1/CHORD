from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from .views import (
    DashboardView,
    ProfileUpdateView,
    UserCreateView,
    UserListView,
    UserUpdateView,
)

app_name = "accounts"

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", ProfileUpdateView.as_view(), name="profile"),
    path(
        "password/change/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/password_change_form.html",
            success_url=reverse_lazy("accounts:password-change-done"),
        ),
        name="password-change",
    ),
    path(
        "password/change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="registration/password_change_done.html"
        ),
        name="password-change-done",
    ),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/add/", UserCreateView.as_view(), name="user-add"),
    path("users/<int:pk>/edit/", UserUpdateView.as_view(), name="user-edit"),
]
