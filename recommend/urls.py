from django.urls import path

from . import views

app_name = "recommend"
urlpatterns = [
    path("", views.MainMenuView.as_view(), name="index"),
    path("remove/<int:pk>", views.RemovePaperView.as_view(), name="remove")
]
