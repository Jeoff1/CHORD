from django import forms

from apps.members.models import Member

from .models import Contribution, Fund


class FundForm(forms.ModelForm):
    class Meta:
        model = Fund
        fields = ("name", "description", "is_active")
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

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

    def clean_reference(self):
        return self.cleaned_data["reference"].strip()
