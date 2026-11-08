from django import forms

from .models import Member


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = (
            "user",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "address",
            "date_of_birth",
            "membership_status",
            "joined_on",
        )
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "date_of_birth": forms.DateInput(attrs={"type": "date"}),
            "joined_on": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()
