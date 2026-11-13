from django.urls import path

from .views import (
    ChurchRecordCreateView,
    ChurchRecordDetailView,
    ChurchRecordListView,
    ChurchRecordUpdateView,
)

app_name = "records"

urlpatterns = [
    path("", ChurchRecordListView.as_view(), name="list"),
    path("add/", ChurchRecordCreateView.as_view(), name="add"),
    path("<uuid:public_id>/", ChurchRecordDetailView.as_view(), name="detail"),
    path("<uuid:public_id>/edit/", ChurchRecordUpdateView.as_view(), name="edit"),
]
