from django import forms

from apps.ministries.models import Ministry
from apps.ministries.services import led_ministry_ids

from .models import Event, EventParticipant
from .services import participant_member_queryset


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"

    def __init__(self, **kwargs):
        kwargs.setdefault("format", "%Y-%m-%dT%H:%M")
        super().__init__(**kwargs)


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = (
            "title",
            "description",
            "event_type",
            "ministry",
            "starts_at",
            "ends_at",
            "location",
            "status",
            "visibility",
            "registration_required",
            "registration_deadline",
            "capacity",
        )
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
            "starts_at": DateTimeLocalInput(),
            "ends_at": DateTimeLocalInput(),
            "registration_deadline": DateTimeLocalInput(),
        }

    def __init__(self, *args, actor, **kwargs):
        super().__init__(*args, **kwargs)
        self.actor = actor
        ministries = Ministry.objects.filter(status=Ministry.Status.ACTIVE)
        if not actor.has_perm("events.manage_events"):
            ministries = ministries.filter(pk__in=led_ministry_ids(actor))
        self.fields["ministry"].queryset = ministries

    def clean(self):
        cleaned_data = super().clean()
        ministry = cleaned_data.get("ministry")
        if not self.actor.has_perm("events.manage_events") and ministry is None:
            self.add_error(
                "ministry", "Ministry Leaders must select an assigned ministry."
            )
        if not cleaned_data.get("registration_required"):
            cleaned_data["registration_deadline"] = None
            cleaned_data["capacity"] = None
        return cleaned_data


class EventParticipantForm(forms.ModelForm):
    class Meta:
        model = EventParticipant
        fields = ("member", "registration_status", "notes")

    def __init__(self, *args, event, actor, **kwargs):
        super().__init__(*args, **kwargs)
        self.event = event
        self.actor = actor
        self.instance.event = event
        unavailable = event.participants.exclude(pk=self.instance.pk).values(
            "member_id"
        )
        self.fields["member"].queryset = participant_member_queryset(event).exclude(
            pk__in=unavailable
        )
        if self.instance.pk:
            self.fields["member"].disabled = True

    def save(self, commit=True):
        participant = super().save(commit=False)
        participant.event = self.event
        if not participant.registered_by_id:
            participant.registered_by = self.actor
        if commit:
            participant.save()
        return participant


class AttendanceEntryForm(forms.Form):
    participant = forms.ModelChoiceField(
        queryset=EventParticipant.objects.none(),
        widget=forms.HiddenInput,
    )
    attendance_status = forms.ChoiceField(
        choices=EventParticipant.AttendanceStatus.choices
    )

    def __init__(self, *args, participant_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        if participant_queryset is not None:
            self.fields["participant"].queryset = participant_queryset


AttendanceFormSet = forms.formset_factory(AttendanceEntryForm, extra=0)
