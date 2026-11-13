from django.urls import path

from .views import (
    ChurchCalendarView,
    ChurchProfileUpdateView,
    OccasionUpdateView,
    SeasonUpdateView,
)

app_name = "traditions"

urlpatterns = [
    path("", ChurchProfileUpdateView.as_view(), name="church-profile"),
    path("calendar/", ChurchCalendarView.as_view(), name="calendar"),
    path("calendar/seasons/<int:pk>/", SeasonUpdateView.as_view(), name="season-edit"),
    path(
        "calendar/occasions/<int:pk>/",
        OccasionUpdateView.as_view(),
        name="occasion-edit",
    ),
]
