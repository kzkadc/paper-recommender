from django.urls import path

from . import views

app_name = "user"
urlpatterns = [
    path("login", views.Login.as_view(), name="login"),
    path("logout", views.Logout.as_view(), name="logout"),
    path("signup", views.Signup.as_view(), name="signup"),
    path("setting", views.UserSetting.as_view(), name="setting")
]
