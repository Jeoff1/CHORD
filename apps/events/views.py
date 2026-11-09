from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.accounts.mixins import AuthenticatedPermissionRequiredMixin
from apps.ministries.models import Ministry

from .forms import AttendanceFormSet, EventForm, EventParticipantForm
from .models import Event, EventParticipant
from .services import (
    can_manage_event,
    cancel_registration,
    record_event_attendance,
    register_member,
    synchronize_linked_schedules,
    visible_events_for,
)


class EventListView(AuthenticatedPermissionRequiredMixin, ListView):
    permission_required = "events.view_event_calendar"
    model = Event
    template_name = "events/event_list.html"
    context_object_name = "events"
    paginate_by = 25

    def get_queryset(self):
        queryset = visible_events_for(self.request.user)
        query = self.request.GET.get("q", "").strip()
        event_type = self.request.GET.get("type", "").strip()
        ministry = self.request.GET.get("ministry", "").strip()
        timing = self.request.GET.get("timing", "upcoming")
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
                | Q(description__icontains=query)
                | Q(location__icontains=query)
            )
        if event_type in Event.Type.values:
            queryset = queryset.filter(event_type=event_type)
        if ministry.isdigit():
            queryset = queryset.filter(ministry_id=ministry)
        if timing == "upcoming":
            queryset = queryset.filter(ends_at__gte=timezone.now())
        elif timing == "past":
            queryset = queryset.filter(ends_at__lt=timezone.now()).order_by(
                "-starts_at"
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        params = self.request.GET.copy()
        params.pop("page", None)
        context.update(
            {
                "query": self.request.GET.get("q", ""),
                "selected_type": self.request.GET.get("type", ""),
                "selected_ministry": self.request.GET.get("ministry", ""),
                "selected_timing": self.request.GET.get("timing", "upcoming"),
                "type_choices": Event.Type.choices,
                "ministries": Ministry.objects.filter(status=Ministry.Status.ACTIVE),
                "pagination_query": params.urlencode(),
            }
        )
        return context


class EventDetailView(AuthenticatedPermissionRequiredMixin, DetailView):
    permission_required = "events.view_event_calendar"
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"
    slug_field = "public_id"
    slug_url_kwarg = "public_id"

    def get_queryset(self):
        return visible_events_for(self.request.user).prefetch_related(
            "participants__member"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["can_manage"] = can_manage_event(self.request.user, self.object)
        try:
            member = self.request.user.member_record
        except ObjectDoesNotExist:
            member = None
        context["member"] = member
        context["own_participation"] = (
            self.object.participants.filter(member=member).first() if member else None
        )
        if context["can_manage"]:
            context["participants"] = self.object.participants.select_related("member")
        return context


class EventManageMixin(AuthenticatedPermissionRequiredMixin):
    model = Event
    form_class = EventForm
    template_name = "events/event_form.html"
    slug_field = "public_id"
    slug_url_kwarg = "public_id"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["actor"] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse("events:detail", args=(self.object.public_id,))

    def form_valid(self, form):
        response = super().form_valid(form)
        synchronize_linked_schedules(self.object)
        return response


class EventCreateView(EventManageMixin, CreateView):
    permission_required = (
        "events.manage_ministry_events",
        "events.add_event",
    )

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "The event was created.")
        return super().form_valid(form)


class EventUpdateView(EventManageMixin, UpdateView):
    permission_required = (
        "events.manage_ministry_events",
        "events.change_event",
    )

    def get_object(self, queryset=None):
        event = super().get_object(queryset)
        if not can_manage_event(self.request.user, event):
            raise PermissionDenied
        return event

    def form_valid(self, form):
        messages.success(self.request, "The event was updated.")
        return super().form_valid(form)


class EventRegistrationView(AuthenticatedPermissionRequiredMixin, View):
    permission_required = "events.register_for_events"

    def post(self, request, *args, **kwargs):
        event = get_object_or_404(
            visible_events_for(request.user),
            public_id=kwargs["public_id"],
        )
        try:
            member = request.user.member_record
        except ObjectDoesNotExist as error:
            raise PermissionDenied from error
        action = request.POST.get("action", "register")
        try:
            if action == "cancel":
                cancel_registration(event=event, member=member)
                messages.success(request, "Your event registration was cancelled.")
            else:
                participant = register_member(
                    event=event,
                    member=member,
                    actor=request.user,
                )
                messages.success(
                    request,
                    f"Your registration status is {participant.get_registration_status_display().lower()}.",
                )
        except EventParticipant.DoesNotExist:
            messages.error(request, "No active registration was found.")
        except ValidationError as error:
            messages.error(request, "; ".join(error.messages))
        return redirect("events:detail", public_id=event.public_id)


class ParticipantManageMixin(AuthenticatedPermissionRequiredMixin):
    model = EventParticipant
    form_class = EventParticipantForm
    template_name = "events/participant_form.html"

    def get_event(self):
        if not hasattr(self, "event"):
            self.event = get_object_or_404(Event, public_id=self.kwargs["public_id"])
            if not can_manage_event(self.request.user, self.event):
                raise PermissionDenied
        return self.event

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(event=self.get_event(), actor=self.request.user)
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["event"] = self.get_event()
        return context

    def get_success_url(self):
        return reverse("events:detail", args=(self.get_event().public_id,))


class ParticipantCreateView(ParticipantManageMixin, CreateView):
    permission_required = (
        "events.manage_ministry_events",
        "events.add_eventparticipant",
    )

    def form_valid(self, form):
        messages.success(self.request, "The event participant was added.")
        return super().form_valid(form)


class ParticipantUpdateView(ParticipantManageMixin, UpdateView):
    permission_required = (
        "events.manage_ministry_events",
        "events.change_eventparticipant",
    )

    def get_object(self, queryset=None):
        return get_object_or_404(
            EventParticipant,
            pk=self.kwargs["pk"],
            event=self.get_event(),
        )

    def form_valid(self, form):
        messages.success(self.request, "The event participant was updated.")
        return super().form_valid(form)


class EventAttendanceView(AuthenticatedPermissionRequiredMixin, View):
    permission_required = (
        "events.record_event_attendance",
        "events.change_eventparticipant",
    )
    template_name = "events/attendance_form.html"

    def get_event(self):
        event = get_object_or_404(Event, public_id=self.kwargs["public_id"])
        if not can_manage_event(self.request.user, event):
            raise PermissionDenied
        return event

    def get_participants(self, event):
        return event.participants.exclude(
            registration_status=EventParticipant.RegistrationStatus.CANCELLED
        ).select_related("member")

    def get_initial(self, participants):
        return [
            {
                "participant": participant,
                "attendance_status": participant.attendance_status,
            }
            for participant in participants
        ]

    def get(self, request, *args, **kwargs):
        event = self.get_event()
        participants = self.get_participants(event)
        formset = AttendanceFormSet(
            initial=self.get_initial(participants),
            form_kwargs={"participant_queryset": participants},
        )
        return render(request, self.template_name, {"event": event, "formset": formset})

    def post(self, request, *args, **kwargs):
        event = self.get_event()
        participants = self.get_participants(event)
        formset = AttendanceFormSet(
            request.POST,
            form_kwargs={"participant_queryset": participants},
        )
        if formset.is_valid():
            record_event_attendance(
                event=event,
                entries=formset.cleaned_data,
                actor=request.user,
            )
            messages.success(request, "Event attendance was recorded.")
            return redirect("events:detail", public_id=event.public_id)
        return render(request, self.template_name, {"event": event, "formset": formset})
