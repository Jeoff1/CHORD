from django import forms

from apps.members.models import Member

from .models import Contribution, Fund


class FundForm(forms.ModelForm):
    class Meta:
        model = Fund
        fields = ("name", "description", "is_active")
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_control_classes(self.fields)

    def clean_name(self):
        return self.cleaned_data["name"].strip()


class ContributionForm(forms.ModelForm):
    class Meta:
        model = Contribution
        fields = (
            "member",
            "anonymous_donor",
            "fund",
            "amount",
            "contributed_on",
            "method",
            "reference",
            "notes",
        )
        widgets = {
            "contributed_on": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "anonymous_donor": "Record as anonymous",
            "contributed_on": "Contribution date",
            "reference": "Reference or receipt number",
            "notes": "Internal notes",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["member"].queryset = Member.objects.exclude(
            membership_status=Member.Status.INACTIVE
        )
        if self.instance.pk and self.instance.member_id:
            self.fields["member"].queryset = (
                Member.objects.filter(pk=self.instance.member_id)
                | self.fields["member"].queryset
            )
        self.fields["fund"].queryset = Fund.objects.filter(is_active=True)
        if self.instance.pk and self.instance.fund_id:
            self.fields["fund"].queryset = (
                Fund.objects.filter(pk=self.instance.fund_id)
                | self.fields["fund"].queryset
            )
        apply_control_classes(self.fields)

    def clean_reference(self):
        return self.cleaned_data["reference"].strip()


def apply_control_classes(fields):
    for field in fields.values():
        if isinstance(field.widget, forms.CheckboxInput):
            class_name = "form-check-input"
        elif isinstance(field.widget, forms.Select):
            class_name = "form-select"
        else:
            class_name = "form-control"
        field.widget.attrs.setdefault("class", class_name)
