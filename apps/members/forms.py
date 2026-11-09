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
        labels = {
            "email": "Email address",
            "phone_number": "Mobile number",
            "joined_on": "Member since",
            "user": "Linked CHORD account",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            class_name = (
                "form-select"
                if isinstance(field.widget, forms.Select)
                else "form-control"
            )
            field.widget.attrs.setdefault("class", class_name)

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()
