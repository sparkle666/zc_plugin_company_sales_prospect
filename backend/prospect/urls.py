from django.urls import path
from .views import (
    ProspectsUpdateView,
    SearchProspects,
    ProspectsCreateView,
    WelcomeView,
    ProspectsListView,
    ProspectsDeleteView,
)


urlpatterns = [
    path("search/<str:search>/", SearchProspects, name="search"),
    path("create/", ProspectsCreateView.as_view()),
    path("", ProspectsListView.as_view(), name="prospects"),
    path("welcome/", WelcomeView.as_view(), name="welcome_mail"),
    path("update/<str:pk>/", ProspectsUpdateView.as_view()),
    path("delete/<str:pk>/", ProspectsDeleteView.as_view()),
]
