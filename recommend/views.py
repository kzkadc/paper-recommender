from django.shortcuts import render, redirect
from django.views import View
from django.http.request import HttpRequest
from django.http.response import HttpResponse

from .models import UserPaper
from .forms import AddPaperForm


class MainMenuView(View):
    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect("user:login")

        papers = UserPaper.objects.filter(owner=request.user)

        if "form" in kwargs:
            form = kwargs["form"]
        else:
            form = AddPaperForm()
        return render(request, "main_menu.html", {
            "user": request.user,
            "form": form,
            "papers": papers
        })

    def post(self, request: HttpRequest) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect("user:login")

        form = AddPaperForm(data=request.POST)
        if form.is_valid():
            userpaper: UserPaper = form.save(commit=False)
            userpaper.owner = request.user
            userpaper.save()
            return self.get(request)
        else:
            return self.get(request, form=form)


class RemovePaperView(View):
    def get(self, request: HttpRequest, **kwargs) -> HttpRequest:
        if not request.user.is_authenticated:
            return redirect("user:login")

        try:
            paper: UserPaper = UserPaper.objects.get(
                owner=request.user, pk=kwargs["pk"])
        except UserPaper.DoesNotExist:
            return redirect("recommend:index")
        else:
            paper.delete()

        return redirect("recommend:index")
