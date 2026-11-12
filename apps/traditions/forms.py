from django import forms

from .models import ChurchProfile


class ChurchProfileForm(forms.ModelForm):
    class Meta:
        model = ChurchProfile
        fields = ["name", "tradition"]
        labels = {"name": "Church name"}
        help_texts = {
            "tradition": "Switching tradition keeps all existing data.",
        }
