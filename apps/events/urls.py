from django.urls import path

from .views import (
    EventAttendanceView,
    EventCreateView,
    EventDetailView,
    EventListView,
    EventRegistrationView,
    EventUpdateView,
    ParticipantCreateView,
    ParticipantUpdateView,
)

app_name = "events"

urlpatterns = [
    path("", EventListView.as_view(), name="list"),
    path("add/", EventCreateView.as_view(), name="add"),
    path("<uuid:public_id>/", EventDetailView.as_view(), name="detail"),
    path("<uuid:public_id>/edit/", EventUpdateView.as_view(), name="edit"),
    path(
        "<uuid:public_id>/registration/",
        EventRegistrationView.as_view(),
        name="registration",
    ),
    path(
        "<uuid:public_id>/participants/add/",
        ParticipantCreateView.as_view(),
        name="participant-add",
    ),
    path(
        "<uuid:public_id>/participants/<int:pk>/edit/",
        ParticipantUpdateView.as_view(),
        name="participant-edit",
    ),
    path(
        "<uuid:public_id>/attendance/",
        EventAttendanceView.as_view(),
        name="attendance",
    ),
]
