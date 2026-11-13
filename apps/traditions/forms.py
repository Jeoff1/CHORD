from django import forms

from . import services
from .models import ChurchProfile


class ChurchProfileForm(forms.ModelForm):
    enabled_modules = forms.MultipleChoiceField(
        choices=list(services.MODULES.items()),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Enabled modules",
        help_text="Disabled modules disappear from navigation for everyone.",
    )

    class Meta:
        model = ChurchProfile
        fields = ["name", "tradition"]
        labels = {"name": "Church name"}
        help_texts = {
            "tradition": "Switching tradition keeps all existing data.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial["enabled_modules"] = sorted(
                services.enabled_modules(self.instance)
            )

    def save(self, commit=True):
        self.instance.module_overrides = services.module_overrides_for(
            self.cleaned_data["tradition"], set(self.cleaned_data["enabled_modules"])
        )
        return super().save(commit)


class CalendarDatesForm(forms.ModelForm):
    """Edits only the dates, so movable feasts can be corrected each year."""

    class Meta:
        fields = ["start_date", "end_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "end_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }
