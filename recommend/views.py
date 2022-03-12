from typing import Any
from django.shortcuts import render, redirect
from django.views import View
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.db.models import QuerySet

import pandas as pd

from .models import Paper, UserPaper, Conference, ReferencePaper
from .forms import AddPaperForm


class MainMenuView(View):
    def get(self, request: HttpRequest, *args: tuple, **kwargs: dict[str, Any]) -> HttpResponse:
        if not request.user.is_authenticated:
            return redirect("user:login")

        papers = UserPaper.objects.filter(owner=request.user)

        if "form" in kwargs:
            form = kwargs["form"]
        else:
            form = AddPaperForm()

        conferences = Conference.objects.all()

        return render(request, "main_menu.html", {
            "user": request.user,
            "form": form,
            "papers": papers,
            "conferences": conferences
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


class RecommendationView(View):
    def get(self, request: HttpRequest, **kwargs: dict[str, Any]) -> HttpRequest:
        try:
            conference = Conference.objects.get(pk=kwargs["pk"])
        except Conference.DoesNotExist:
            return redirect("recommend:index")

        ref_papers = ReferencePaper.objects.filter(published_at=conference)
        if "display_num" in kwargs:
            ref_papers = ref_papers[:kwargs["display_num"]]

        temp_dict = {
            "title": [],
            "abstract": [],
            "pk": [],
            "url": []
        }
        p: ReferencePaper
        for p in ref_papers:
            temp_dict["title"].append(p.title)
            temp_dict["abstract"].append(p.abstract)
            temp_dict["pk"].append(p.pk)
            temp_dict["url"].append(p.url)
        ref_df = pd.DataFrame(temp_dict)

        user_papers = UserPaper.objects.filter(owner=request.user)
        temp_dict = {
            "title": [],
            "abstract": []
        }
        p: UserPaper
        for p in user_papers:
            temp_dict["title"].append(p.title)
            temp_dict["abstract"].append(p.abstract)
        user_df = pd.DataFrame(temp_dict)

        ref_df = self.sort_papers(ref_df, user_df)

        return render(request, "recommend_list.html", {
            "conference": conference,
            "papers": ref_df
        })

    def sort_papers(self, ref_df: pd.DataFrame, user_df: pd.DataFrame) -> pd.DataFrame:
        ref_df["distance"] = 100
        return ref_df
