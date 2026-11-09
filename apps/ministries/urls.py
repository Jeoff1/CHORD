from django.urls import path

from .views import (
    MembershipCreateView,
    MembershipUpdateView,
    MinistryCreateView,
    MinistryDetailView,
    MinistryListView,
    MinistryUpdateView,
)

app_name = "ministries"

urlpatterns = [
    path("", MinistryListView.as_view(), name="list"),
    path("add/", MinistryCreateView.as_view(), name="add"),
    path("<uuid:public_id>/", MinistryDetailView.as_view(), name="detail"),
    path("<uuid:public_id>/edit/", MinistryUpdateView.as_view(), name="edit"),
    path(
        "<uuid:public_id>/members/add/",
        MembershipCreateView.as_view(),
        name="membership-add",
    ),
    path(
        "<uuid:public_id>/members/<int:pk>/edit/",
        MembershipUpdateView.as_view(),
        name="membership-edit",
    ),
]
