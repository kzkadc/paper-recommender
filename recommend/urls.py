from django.urls import path

from . import views

app_name = "recommend"
urlpatterns = [
    path("", views.MainMenuView.as_view(), name="index"),
    path("remove/<int:pk>", views.RemovePaperView.as_view(), name="remove"),
    path("add_favorite",
         views.AddFavoritePaperView.as_view(), name="add_favorite"),
    path("<int:pk>/<int:display_num>",
         views.RecommendationView.as_view(), name="get_recommendation"),
    path("<int:pk>",
         views.RecommendationView.as_view(), name="get_recommendation"),

]
