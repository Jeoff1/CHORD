from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import Profile, Role, UserRole

User = get_user_model()


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("preferred_name", "phone_number")


class RoleAssignmentMixin:
    roles = forms.ModelMultipleChoiceField(
        queryset=Role.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    def __init__(self, *args, actor=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor = actor
        if self.instance.pk:
            self.fields["roles"].initial = self.instance.roles.all()

        if self.actor == self.instance:
            self.fields["roles"].disabled = True
            self.fields["is_active"].disabled = True

    def _save_roles(self, user):
        selected_roles = set(self.cleaned_data["roles"])
        existing_roles = set(user.roles.all())
        UserRole.objects.filter(
            user=user,
            role__in=existing_roles - selected_roles,
        ).delete()
        UserRole.objects.bulk_create(
            [
                UserRole(user=user, role=role, assigned_by=self.actor)
                for role in selected_roles - existing_roles
            ]
        )


class ManagedUserCreationForm(RoleAssignmentMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "roles",
        )

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            self._save_roles(user)
        return user


class ManagedUserUpdateForm(RoleAssignmentMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "roles",
        )

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            self._save_roles(user)
        return user
