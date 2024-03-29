import re
from typing import Any, Iterable

from django.shortcuts import get_object_or_404, render, redirect
from django.views import View
from django.http.request import HttpRequest
from django.http.response import HttpResponse, JsonResponse
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet

import pandas as pd
import numpy as np
import fasttext

from paper_recommender.local_settings import FASTTEXT_MODEL, STOPWORDS
from .models import UserPaper, ConferenceName, Conference, ReferencePaper
from .forms import AddPaperForm


class MainMenuView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, *args: tuple, **kwargs: dict[str, Any]) -> HttpResponse:
        papers = UserPaper.objects.filter(owner=request.user) \
            .order_by("added_at").reverse()

        if "form" in kwargs:
            form = kwargs["form"]
        else:
            form = AddPaperForm()

        conferences = ConferenceName.objects.all().order_by("name")

        return render(request, "main_menu.html", {
            "user": request.user,
            "form": form,
            "papers": papers,
            "conferences": conferences
        })

    def post(self, request: HttpRequest) -> HttpResponse:
        form = AddPaperForm(data=request.POST)
        if form.is_valid():
            userpaper: UserPaper = form.save(commit=False)
            userpaper.owner = request.user
            userpaper.added_at = timezone.now()
            userpaper.save()
            return self.get(request)
        else:
            return self.get(request, form=form)


class RemovePaperView(LoginRequiredMixin, View):
    def get(self, request: HttpRequest, **kwargs) -> HttpResponse:
        paper = get_object_or_404(
            UserPaper, owner=request.user, pk=kwargs["pk"])
        paper.delete()

        return redirect("recommend:index")


class AddFavoritePaperView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest, **kwargs) -> JsonResponse:
        pk = int(request.POST.get("pk"))
        paper = get_object_or_404(ReferencePaper, pk=pk)

        UserPaper(
            title=paper.title,
            abstract=paper.abstract,
            owner=request.user,
            memo=f"{paper.url} ({paper.published_at})",
            added_at=timezone.now()
        ).save()

        return JsonResponse({
            "state": "success",
            "pk": pk
        })


class RecommendationView(LoginRequiredMixin, View):
    @classmethod
    def prepare_fasttext_model(cls):
        print("preparing fasttext model...", end="")

        cls.fasttext_model = fasttext.load_model(FASTTEXT_MODEL)
        with open(STOPWORDS, "r", encoding="utf-8") as f:
            cls.stopwords = set(f.read().strip().split("\n"))

        print("done")

    @classmethod
    def embed_text(cls, text: str) -> np.ndarray:
        text = re.sub(r"[\s\n\-.,?!:]+", " ", text.strip().lower())
        text = re.sub("\"", "", text)

        splitted_text: Iterable[str] = text.split(" ")
        splitted_text = filter(lambda x: x not in cls.stopwords, splitted_text)

        count = 0
        mean_vec = np.array(0, dtype=np.float32)
        for x in splitted_text:
            mean_vec = mean_vec + cls.fasttext_model.get_word_vector(x)
            count += 1
        mean_vec /= count
        mean_vec /= np.linalg.norm(mean_vec)

        return mean_vec

    def get(self, request: HttpRequest, **kwargs: dict[str, Any]) -> HttpRequest:
        conference = get_object_or_404(Conference, pk=kwargs["pk"])
        ref_papers: QuerySet[ReferencePaper] = ReferencePaper.objects.filter(
            published_at=conference)

        temp_dict = {
            "title": [],
            "abstract": [],
            "pk": [],
            "url": []
        }
        for p in ref_papers:
            temp_dict["title"].append(p.title)
            temp_dict["abstract"].append(p.abstract)
            temp_dict["pk"].append(p.pk)
            temp_dict["url"].append(p.url)
        ref_df = pd.DataFrame(temp_dict)

        user_papers: QuerySet[UserPaper] = UserPaper.objects.filter(
            owner=request.user)
        temp_dict = {
            "title": [],
            "abstract": []
        }
        for p in user_papers:
            temp_dict["title"].append(p.title)
            temp_dict["abstract"].append(p.abstract)
        user_df = pd.DataFrame(temp_dict)

        if len(ref_df) == 0:
            message = """
                論文がありません。
            """
        elif len(user_df) >= 1:
            ref_df = self.sort_papers(ref_df, user_df)
            message = None
        else:
            ref_df = ref_df.iloc[np.random.permutation(len(ref_df))]
            ref_df["distance"] = -1

            message = """
                お気に入り論文が登録されていません。
                登録するとおすすめ順にソートして表示されます。
            """

        if "display_num" in kwargs:
            ref_df = ref_df.iloc[:kwargs["display_num"]]

        ref_df.reset_index(inplace=True)

        return render(request, "recommend_list.html", {
            "conference": conference,
            "papers": ref_df,
            "message": message
        })

    @classmethod
    def sort_papers(cls, ref_df: pd.DataFrame, user_df: pd.DataFrame) -> pd.DataFrame:
        user_df["temp_text"] = user_df["title"] + " " + user_df["abstract"]
        user_vec: np.ndarray = np.stack(
            user_df["temp_text"].map(cls.embed_text))
        user_df.drop(columns=["temp_text"], inplace=True)

        ref_df["temp_text"] = ref_df["title"] + " " + ref_df["abstract"]
        ref_vec: np.ndarray = np.stack(ref_df["temp_text"].map(cls.embed_text))
        ref_df.drop(columns=["temp_text"], inplace=True)

        ii, jj = np.meshgrid(
            np.arange(user_vec.shape[0]), np.arange(ref_vec.shape[0]))
        dist: np.ndarray = np.square(
            user_vec[ii] - ref_vec[jj]).sum(axis=2)  # (num_ref, num_user)
        dist = dist.min(axis=1)

        ref_df["distance"] = dist
        ref_df.sort_values("distance", inplace=True)

        return ref_df


RecommendationView.prepare_fasttext_model()
