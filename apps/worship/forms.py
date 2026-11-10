from django import forms
from django.db import transaction
from django.db.models import Q

from apps.events.models import Event
from apps.events.services import visible_events_for
from apps.members.models import Member

from .models import (
    ChoirAnnouncement,
    ChoirEnrollment,
    PlanSong,
    Rehearsal,
    RehearsalAttendance,
    Song,
    SongResource,
    WorshipPlan,
)
from .services import sync_plan_participants, sync_song_assignments
from .spotify import normalize_spotify_track


def style_choir_fields(fields):
    """Apply the shared CHORD controls to choir-facing forms."""
    for field in fields.values():
        widget = field.widget
        if isinstance(widget, forms.HiddenInput):
            continue
        if isinstance(widget, forms.CheckboxSelectMultiple):
            widget.attrs.setdefault("class", "chord-choice-list")
        elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
            widget.attrs.setdefault("class", "form-select")
        else:
            widget.attrs.setdefault("class", "form-control")


class DateTimeLocalInput(forms.DateTimeInput):
    input_type = "datetime-local"

    def __init__(self, **kwargs):
        kwargs.setdefault("format", "%Y-%m-%dT%H:%M")
        super().__init__(**kwargs)


class ChoirEnrollmentForm(forms.ModelForm):
    class Meta:
        model = ChoirEnrollment
        fields = ("member", "voice_part", "status", "joined_on", "notes")
        widgets = {
            "joined_on": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_choir_fields(self.fields)
        unavailable_ids = ChoirEnrollment.objects.exclude(pk=self.instance.pk).values(
            "member_id"
        )
        self.fields["member"].queryset = Member.objects.exclude(pk__in=unavailable_ids)
        if self.instance.pk:
            self.fields["member"].disabled = True


class RehearsalForm(forms.ModelForm):
    class Meta:
        model = Rehearsal
        fields = (
            "event",
            "title",
            "starts_at",
            "ends_at",
            "location",
            "status",
            "notes",
            "songs",
        )
        widgets = {
            "starts_at": DateTimeLocalInput(),
            "ends_at": DateTimeLocalInput(),
            "notes": forms.Textarea(attrs={"rows": 4}),
            "songs": forms.SelectMultiple(attrs={"size": 8}),
        }

    def __init__(self, *args, actor, **kwargs):
        super().__init__(*args, **kwargs)
        style_choir_fields(self.fields)
        events = visible_events_for(actor).filter(event_type=Event.Type.REHEARSAL)
        available_events = Q(rehearsal__isnull=True)
        if self.instance.pk:
            available_events |= Q(rehearsal=self.instance)
        events = events.filter(available_events)
        self.fields["event"].queryset = events
        self.fields["starts_at"].required = False
        self.fields["ends_at"].required = False
        self.fields[
            "songs"
        ].help_text = "Select songs whose playback and authorized resources are needed for rehearsal."

    def clean(self):
        cleaned_data = super().clean()
        event = cleaned_data.get("event")
        if event:
            cleaned_data["starts_at"] = event.starts_at
            cleaned_data["ends_at"] = event.ends_at
            cleaned_data["location"] = event.location
        else:
            if not cleaned_data.get("starts_at"):
                self.add_error("starts_at", "Enter a start time or select an event.")
            if not cleaned_data.get("ends_at"):
                self.add_error("ends_at", "Enter an end time or select an event.")
        return cleaned_data


class AttendanceEntryForm(forms.Form):
    enrollment = forms.ModelChoiceField(
        queryset=ChoirEnrollment.objects.none(),
        widget=forms.HiddenInput,
    )
    status = forms.ChoiceField(choices=RehearsalAttendance.Status.choices)
    notes = forms.CharField(max_length=250, required=False)

    def __init__(self, *args, enrollment_queryset=None, **kwargs):
        super().__init__(*args, **kwargs)
        style_choir_fields(self.fields)
        if enrollment_queryset is not None:
            self.fields["enrollment"].queryset = enrollment_queryset


AttendanceFormSet = forms.formset_factory(AttendanceEntryForm, extra=0)


class ChoirAnnouncementForm(forms.ModelForm):
    class Meta:
        model = ChoirAnnouncement
        fields = ("title", "body", "audience", "published_at", "expires_at")
        widgets = {
            "body": forms.Textarea(attrs={"rows": 5}),
            "published_at": DateTimeLocalInput(),
            "expires_at": DateTimeLocalInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        style_choir_fields(self.fields)


class SongForm(forms.ModelForm):
    spotify_track = forms.CharField(
        required=False,
        label="Spotify track",
        help_text=(
            "Paste an official Spotify track link, spotify:track URI, or "
            "22-character track ID."
        ),
    )
    theme_list = forms.CharField(
        required=False,
        label="Worship themes",
        help_text="Comma-separated themes, for example: grace, communion, hope.",
    )

    class Meta:
        model = Song
        fields = (
            "title",
            "artist",
            "default_key",
            "tempo_bpm",
            "category",
            "theme_list",
            "spotify_track",
            "notes",
        )
        widgets = {"notes": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["theme_list"].initial = self.instance.theme_text
            self.fields["spotify_track"].initial = self.instance.spotify_url

    def clean_theme_list(self):
        raw_themes = self.cleaned_data["theme_list"]
        themes = []
        for item in raw_themes.split(","):
            theme = " ".join(item.strip().lower().split())
            if theme and theme not in themes:
                themes.append(theme)
        if len(themes) > 12:
            raise forms.ValidationError("Use no more than 12 worship themes.")
        if any(len(theme) > 50 for theme in themes):
            raise forms.ValidationError(
                "Each worship theme must be 50 characters or fewer."
            )
        return themes

    def clean_spotify_track(self):
        return normalize_spotify_track(self.cleaned_data["spotify_track"])

    def save(self, commit=True):
        song = super().save(commit=False)
        song.themes = self.cleaned_data["theme_list"]
        song.spotify_track_id = self.cleaned_data["spotify_track"]
        if commit:
            song.save()
        return song


class SongResourceForm(forms.ModelForm):
    class Meta:
        model = SongResource
        fields = (
            "title",
            "resource_type",
            "file",
            "external_url",
            "authorization_reference",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["file"].help_text = (
            "PDF, text, ChordPro, Word, or image; maximum 10 MiB. "
            "PDF, UTF-8 text, ChordPro, and images can be viewed in CHORD."
        )


class WorshipPlanForm(forms.ModelForm):
    choir_participants = forms.ModelMultipleChoiceField(
        queryset=ChoirEnrollment.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = WorshipPlan
        fields = (
            "event",
            "title",
            "service_datetime",
            "location",
            "status",
            "preparation_notes",
            "choir_participants",
        )
        widgets = {
            "service_datetime": DateTimeLocalInput(),
            "preparation_notes": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, actor, **kwargs):
        super().__init__(*args, **kwargs)
        events = visible_events_for(actor).filter(event_type=Event.Type.WORSHIP_SERVICE)
        available_events = Q(worship_plan__isnull=True)
        if self.instance.pk:
            available_events |= Q(worship_plan=self.instance)
        events = events.filter(available_events)
        self.fields["event"].queryset = events
        self.fields["service_datetime"].required = False
        available_filter = Q(status=ChoirEnrollment.Status.ACTIVE)
        if self.instance.pk:
            available_filter |= Q(plan_participations__plan=self.instance)
        active_enrollments = (
            ChoirEnrollment.objects.filter(available_filter)
            .select_related("member")
            .distinct()
        )
        self.fields["choir_participants"].queryset = active_enrollments
        if self.instance.pk:
            self.fields[
                "choir_participants"
            ].initial = self.instance.choir_participants.all()

    def clean(self):
        cleaned_data = super().clean()
        event = cleaned_data.get("event")
        if event:
            cleaned_data["service_datetime"] = event.starts_at
            cleaned_data["location"] = event.location
        elif not cleaned_data.get("service_datetime"):
            self.add_error(
                "service_datetime",
                "Enter a service time or select a church event.",
            )
        return cleaned_data

    @transaction.atomic
    def save(self, commit=True):
        plan = super().save(commit=False)
        if commit:
            plan.save()
            sync_plan_participants(
                plan=plan,
                enrollments=self.cleaned_data["choir_participants"],
            )
        return plan


class PlanSongForm(forms.ModelForm):
    class Meta:
        model = PlanSong
        fields = ("song", "planned_key", "notes")

    def __init__(self, *args, plan, **kwargs):
        super().__init__(*args, **kwargs)
        self.plan = plan

    def clean_song(self):
        song = self.cleaned_data["song"]
        if self.plan.setlist_items.filter(song=song).exists():
            raise forms.ValidationError("This song is already in the setlist.")
        return song


class SongAssignmentForm(forms.Form):
    enrollments = forms.ModelMultipleChoiceField(
        queryset=ChoirEnrollment.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )
    notes = forms.CharField(max_length=250, required=False)

    def __init__(self, *args, plan_song, actor, **kwargs):
        super().__init__(*args, **kwargs)
        style_choir_fields(self.fields)
        self.plan_song = plan_song
        self.actor = actor
        self.fields["enrollments"].queryset = ChoirEnrollment.objects.filter(
            plan_participations__plan=plan_song.plan,
            status=ChoirEnrollment.Status.ACTIVE,
        ).select_related("member")
        if not self.is_bound:
            self.fields["enrollments"].initial = plan_song.assignments.values_list(
                "enrollment_id", flat=True
            )

    def save(self):
        return sync_song_assignments(
            plan_song=self.plan_song,
            enrollments=self.cleaned_data["enrollments"],
            actor=self.actor,
            notes=self.cleaned_data["notes"],
        )
