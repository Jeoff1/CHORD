from django.urls import path

from .views import (
    AnnouncementCreateView,
    AnnouncementListView,
    AnnouncementUpdateView,
    ChoirActivityView,
    ChoirEnrollmentCreateView,
    ChoirEnrollmentUpdateView,
    ChoirRosterView,
    PlanSongCreateView,
    PlanSongMoveView,
    PlanSongRemoveView,
    RehearsalAttendanceView,
    RehearsalCreateView,
    RehearsalDetailView,
    RehearsalListView,
    RehearsalUpdateView,
    SongAssignmentUpdateView,
    SongCreateView,
    SongDetailView,
    SongListView,
    SongResourceCreateView,
    SongResourceDownloadView,
    SongUpdateView,
    WorshipPlanCreateView,
    WorshipPlanDetailView,
    WorshipPlanListView,
    WorshipPlanUpdateView,
)

app_name = "worship"

urlpatterns = [
    path("choir/", ChoirActivityView.as_view(), name="choir-activity"),
    path("choir/roster/", ChoirRosterView.as_view(), name="choir-roster"),
    path("choir/roster/add/", ChoirEnrollmentCreateView.as_view(), name="choir-enroll"),
    path(
        "choir/roster/<uuid:public_id>/edit/",
        ChoirEnrollmentUpdateView.as_view(),
        name="choir-enrollment-edit",
    ),
    path("choir/rehearsals/", RehearsalListView.as_view(), name="rehearsal-list"),
    path("choir/rehearsals/add/", RehearsalCreateView.as_view(), name="rehearsal-add"),
    path(
        "choir/rehearsals/<uuid:public_id>/",
        RehearsalDetailView.as_view(),
        name="rehearsal-detail",
    ),
    path(
        "choir/rehearsals/<uuid:public_id>/edit/",
        RehearsalUpdateView.as_view(),
        name="rehearsal-edit",
    ),
    path(
        "choir/rehearsals/<uuid:public_id>/attendance/",
        RehearsalAttendanceView.as_view(),
        name="rehearsal-attendance",
    ),
    path(
        "choir/announcements/", AnnouncementListView.as_view(), name="announcement-list"
    ),
    path(
        "choir/announcements/add/",
        AnnouncementCreateView.as_view(),
        name="announcement-add",
    ),
    path(
        "choir/announcements/<int:pk>/edit/",
        AnnouncementUpdateView.as_view(),
        name="announcement-edit",
    ),
    path("songs/", SongListView.as_view(), name="song-list"),
    path("songs/add/", SongCreateView.as_view(), name="song-add"),
    path("songs/<uuid:public_id>/", SongDetailView.as_view(), name="song-detail"),
    path("songs/<uuid:public_id>/edit/", SongUpdateView.as_view(), name="song-edit"),
    path(
        "songs/<uuid:public_id>/resources/add/",
        SongResourceCreateView.as_view(),
        name="song-resource-add",
    ),
    path(
        "song-resources/<int:pk>/download/",
        SongResourceDownloadView.as_view(),
        name="song-resource-download",
    ),
    path("plans/", WorshipPlanListView.as_view(), name="plan-list"),
    path("plans/add/", WorshipPlanCreateView.as_view(), name="plan-add"),
    path(
        "plans/<uuid:public_id>/", WorshipPlanDetailView.as_view(), name="plan-detail"
    ),
    path(
        "plans/<uuid:public_id>/edit/",
        WorshipPlanUpdateView.as_view(),
        name="plan-edit",
    ),
    path(
        "plans/<uuid:public_id>/songs/add/",
        PlanSongCreateView.as_view(),
        name="plan-song-add",
    ),
    path(
        "plans/<uuid:public_id>/songs/<int:pk>/move/<str:direction>/",
        PlanSongMoveView.as_view(),
        name="plan-song-move",
    ),
    path(
        "plans/<uuid:public_id>/songs/<int:pk>/remove/",
        PlanSongRemoveView.as_view(),
        name="plan-song-remove",
    ),
    path(
        "plans/<uuid:public_id>/songs/<int:pk>/assignments/",
        SongAssignmentUpdateView.as_view(),
        name="song-assignments",
    ),
]
