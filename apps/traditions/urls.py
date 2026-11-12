from django.urls import path

from .views import ChurchProfileUpdateView

app_name = "traditions"

urlpatterns = [
    path("", ChurchProfileUpdateView.as_view(), name="church-profile"),
]
