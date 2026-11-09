from django.urls import path

from .views import (
    ContributionCreateView,
    ContributionListView,
    ContributionUpdateView,
    FundCreateView,
    FundListView,
    FundUpdateView,
    MyContributionListView,
)

app_name = "giving"

urlpatterns = [
    path("", ContributionListView.as_view(), name="contribution-list"),
    path("add/", ContributionCreateView.as_view(), name="contribution-add"),
    path("mine/", MyContributionListView.as_view(), name="my-contributions"),
    path(
        "<uuid:public_id>/edit/",
        ContributionUpdateView.as_view(),
        name="contribution-edit",
    ),
    path("funds/", FundListView.as_view(), name="fund-list"),
    path("funds/add/", FundCreateView.as_view(), name="fund-add"),
    path("funds/<int:pk>/edit/", FundUpdateView.as_view(), name="fund-edit"),
]
