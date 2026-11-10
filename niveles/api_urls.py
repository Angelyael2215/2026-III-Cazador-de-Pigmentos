from django.urls import path

from .api_views import LevelListView, SubmitAnswerView


urlpatterns = [
    path("levels/", LevelListView.as_view(), name="api-level-list"),
    path(
        "levels/<int:number>/submit/",
        SubmitAnswerView.as_view(),
        name="api-level-submit",
    ),
]
