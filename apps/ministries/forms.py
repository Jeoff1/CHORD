from django import forms

from apps.members.models import Member

from .models import Ministry, MinistryMembership


class MinistryForm(forms.ModelForm):
    class Meta:
        model = Ministry
        fields = ("name", "description", "status")
        widgets = {"description": forms.Textarea(attrs={"rows": 5})}


class MinistryMembershipForm(forms.ModelForm):
    class Meta:
        model = MinistryMembership
        fields = ("member", "role", "status", "joined_on", "notes")
        widgets = {
            "joined_on": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, ministry, actor, **kwargs):
        super().__init__(*args, **kwargs)
        self.ministry = ministry
        self.actor = actor
        used_member_ids = (
            MinistryMembership.objects.filter(ministry=ministry)
            .exclude(pk=self.instance.pk)
            .values("member_id")
        )
        self.fields["member"].queryset = Member.objects.exclude(pk__in=used_member_ids)
        if self.instance.pk:
            self.fields["member"].disabled = True
        if not actor.has_perm("ministries.manage_ministries"):
            self.fields["role"].choices = (
                (MinistryMembership.Role.MEMBER, MinistryMembership.Role.MEMBER.label),
            )
            if (
                self.instance.pk
                and self.instance.role == MinistryMembership.Role.LEADER
            ):
                self.fields["role"].disabled = True
                self.fields["status"].disabled = True

    def clean_role(self):
        role = self.cleaned_data["role"]
        if role == MinistryMembership.Role.LEADER and not self.actor.has_perm(
            "ministries.manage_ministries"
        ):
            raise forms.ValidationError(
                "Only a Church Administrator can assign leaders."
            )
        return role

    def save(self, commit=True):
        membership = super().save(commit=False)
        membership.ministry = self.ministry
        membership.assigned_by = self.actor
        if commit:
            membership.save()
        return membership
