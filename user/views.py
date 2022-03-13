from django.shortcuts import render, redirect
from django.views import View
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.contrib import auth
from django.core.exceptions import ValidationError

from .forms import LoginForm, SignupForm, SettingForm


class Login(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("recommend:index")
        else:
            return render(request, "login.html", {"form": LoginForm()})

    def post(self, request: HttpRequest) -> HttpResponse:
        form = LoginForm(data=request.POST)
        if not form.is_valid():
            return render(request, "login.html", {"form": form})

        try:
            form.clean()
        except ValidationError:
            return render(request, "login.html", {"form": form})

        auth.login(request, form.user_cache)
        return redirect("recommend:index")


class Logout(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        auth.logout(request)
        return redirect("user:login")


class Signup(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        if request.user.is_authenticated:
            return redirect("recommend:index")
        else:
            return render(request, "signup.html", {"form": SignupForm()})

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = SignupForm(data=request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)

            return redirect("recommend:index")
        else:
            return render(request, "signup.html", {"form": form})


class UserSetting(View):
    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect("user:login")

        context = {
            "form": SettingForm(request.user)
        }

        if "message" in kwargs:
            context["message"] = kwargs["message"]

        return render(request, "setting.html", context)

    def post(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect("user:login")

        form = SettingForm(request.user, data=request.POST)
        if form.is_valid():
            form.save()
            return self.get(request, message="パスワードを変更しました。")
        else:
            return render(request, "setting.html", {"form": form})
