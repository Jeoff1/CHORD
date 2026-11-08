from django.urls import path

from .views import (
    MemberCreateView,
    MemberDetailView,
    MemberListView,
    MemberUpdateView,
    MyMemberRecordView,
)

app_name = "members"

urlpatterns = [
    path("", MemberListView.as_view(), name="list"),
    path("add/", MemberCreateView.as_view(), name="add"),
    path("me/", MyMemberRecordView.as_view(), name="my-record"),
    path("<uuid:public_id>/", MemberDetailView.as_view(), name="detail"),
    path("<uuid:public_id>/edit/", MemberUpdateView.as_view(), name="edit"),
]
