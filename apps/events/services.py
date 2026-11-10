from django.core.exceptions import ObjectDoesNotExist, PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from apps.ministries.models import MinistryMembership
from apps.ministries.services import led_ministry_ids

from .models import Event, EventParticipant


def visible_events_for(user):
    """Apply event publication, audience, and leadership visibility rules."""
    queryset = Event.objects.select_related("ministry", "created_by")
    if user.has_perm("events.manage_events"):
        return queryset

    try:
        member_id = user.member_record.pk
    except ObjectDoesNotExist:
        member_id = None
    visible_filter = Q(
        status=Event.Status.PUBLISHED,
        visibility=Event.Visibility.CHURCH,
    )
    if member_id:
        member_ministries = MinistryMembership.objects.filter(
            member_id=member_id,
            status=MinistryMembership.Status.ACTIVE,
        ).values_list("ministry_id", flat=True)
        leader_ministries = MinistryMembership.objects.filter(
            member_id=member_id,
            status=MinistryMembership.Status.ACTIVE,
            role=MinistryMembership.Role.LEADER,
        ).values_list("ministry_id", flat=True)
        visible_filter |= Q(
            status=Event.Status.PUBLISHED,
            visibility=Event.Visibility.MINISTRY,
            ministry_id__in=member_ministries,
        )
        visible_filter |= Q(
            status=Event.Status.PUBLISHED,
            visibility=Event.Visibility.LEADERS,
            ministry_id__in=leader_ministries,
        )
        if user.has_perm("events.manage_ministry_events"):
            visible_filter |= Q(ministry_id__in=leader_ministries)
    return queryset.filter(visible_filter).distinct()


def can_manage_event(user, event):
    if user.has_perm("events.manage_events"):
        return True
    return (
        event.ministry_id is not None
        and user.has_perm("events.manage_ministry_events")
        and event.ministry_id in set(led_ministry_ids(user))
    )


def manageable_events_for(user):
    """Return visible events the user is authorized to administer."""
    queryset = visible_events_for(user)
    if user.has_perm("events.manage_events"):
        return queryset
    if not user.has_perm("events.manage_ministry_events"):
        return queryset.none()
    return queryset.filter(ministry_id__in=led_ministry_ids(user))


def participant_member_queryset(event):
    from apps.members.models import Member

    queryset = Member.objects.exclude(membership_status=Member.Status.INACTIVE)
    if event.visibility != Event.Visibility.CHURCH:
        queryset = queryset.filter(
            ministry_memberships__ministry=event.ministry,
            ministry_memberships__status=MinistryMembership.Status.ACTIVE,
        )
    if event.visibility == Event.Visibility.LEADERS:
        queryset = queryset.filter(
            ministry_memberships__ministry=event.ministry,
            ministry_memberships__role=MinistryMembership.Role.LEADER,
            ministry_memberships__status=MinistryMembership.Status.ACTIVE,
        )
    return queryset.distinct()


@transaction.atomic
def register_member(*, event, member, actor):
    locked_event = Event.objects.select_for_update().get(pk=event.pk)
    if locked_event.status != Event.Status.PUBLISHED:
        raise ValidationError("Registration is available only for published events.")
    if not locked_event.registration_required:
        raise ValidationError("This event does not use registration.")
    now = timezone.now()
    if locked_event.starts_at <= now:
        raise ValidationError("Registration is closed because the event has started.")
    if locked_event.registration_deadline and locked_event.registration_deadline < now:
        raise ValidationError("The registration deadline has passed.")
    if not participant_member_queryset(locked_event).filter(pk=member.pk).exists():
        raise PermissionDenied

    registered_count = locked_event.participants.filter(
        registration_status=EventParticipant.RegistrationStatus.REGISTERED
    ).count()
    status = EventParticipant.RegistrationStatus.REGISTERED
    if locked_event.capacity and registered_count >= locked_event.capacity:
        status = EventParticipant.RegistrationStatus.WAITLISTED
    participant, _ = EventParticipant.objects.update_or_create(
        event=locked_event,
        member=member,
        defaults={
            "registration_status": status,
            "registered_by": actor,
        },
    )
    return participant


@transaction.atomic
def cancel_registration(*, event, member):
    locked_event = Event.objects.select_for_update().get(pk=event.pk)
    participant = EventParticipant.objects.select_for_update().get(
        event=locked_event,
        member=member,
    )
    was_registered = (
        participant.registration_status
        == EventParticipant.RegistrationStatus.REGISTERED
    )
    participant.registration_status = EventParticipant.RegistrationStatus.CANCELLED
    participant.save(update_fields=("registration_status", "updated_at"))
    if was_registered and locked_event.capacity:
        next_waitlisted = (
            EventParticipant.objects.select_for_update()
            .filter(
                event=locked_event,
                registration_status=EventParticipant.RegistrationStatus.WAITLISTED,
            )
            .order_by("registered_at", "id")
            .first()
        )
        if next_waitlisted:
            next_waitlisted.registration_status = (
                EventParticipant.RegistrationStatus.REGISTERED
            )
            next_waitlisted.save(update_fields=("registration_status", "updated_at"))
    return participant


@transaction.atomic
def record_event_attendance(*, event, entries, actor):
    Event.objects.select_for_update().get(pk=event.pk)
    recorded_at = timezone.now()
    for entry in entries:
        participant = entry["participant"]
        participant.attendance_status = entry["attendance_status"]
        participant.attendance_recorded_by = actor
        participant.attendance_recorded_at = recorded_at
        participant.save(
            update_fields=(
                "attendance_status",
                "attendance_recorded_by",
                "attendance_recorded_at",
                "updated_at",
            )
        )


def synchronize_linked_schedules(event):
    """Keep Phase 4 schedule fields aligned when an event is canonical."""
    try:
        plan = event.worship_plan
    except ObjectDoesNotExist:
        plan = None
    if plan:
        plan.service_datetime = event.starts_at
        plan.location = event.location
        plan.save(update_fields=("service_datetime", "location", "updated_at"))

    try:
        rehearsal = event.rehearsal
    except ObjectDoesNotExist:
        rehearsal = None
    if rehearsal:
        rehearsal.starts_at = event.starts_at
        rehearsal.ends_at = event.ends_at
        rehearsal.location = event.location
        rehearsal.save(update_fields=("starts_at", "ends_at", "location", "updated_at"))
