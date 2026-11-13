from django.db import transaction
from django.db.models import Max

from apps.members.models import Member
from apps.traditions.services import users_with_permission

from .models import (
    PlanChoirParticipation,
    PlanSong,
    Rehearsal,
    RehearsalAttendance,
    SongAssignment,
    SongResource,
    WorshipPlan,
)


@transaction.atomic
def save_song_resource(*, form, song, actor):
    """Save a resource and remove a replaced private file after commit."""
    previous_name = ""
    if form.instance.pk:
        previous = (
            SongResource.objects.select_for_update()
            .only("file")
            .get(pk=form.instance.pk)
        )
        previous_name = previous.file.name if previous.file else ""

    resource = form.save(commit=False)
    resource.song = song
    if not resource.added_by_id:
        resource.added_by = actor
    resource.updated_by = actor
    resource.save()

    current_name = resource.file.name if resource.file else ""
    if previous_name and previous_name != current_name:
        storage = SongResource._meta.get_field("file").storage
        transaction.on_commit(lambda: storage.delete(previous_name))
    return resource


@transaction.atomic
def sync_plan_participants(*, plan, enrollments):
    """Synchronize plan participants and discard assignments made invalid by removal."""
    WorshipPlan.objects.select_for_update().get(pk=plan.pk)
    selected_ids = {enrollment.pk for enrollment in enrollments}
    removed_ids = set(
        plan.choir_participations.exclude(enrollment_id__in=selected_ids).values_list(
            "enrollment_id", flat=True
        )
    )
    if removed_ids:
        SongAssignment.objects.filter(
            plan_song__plan=plan,
            enrollment_id__in=removed_ids,
        ).delete()
        plan.choir_participations.filter(enrollment_id__in=removed_ids).delete()

    existing_ids = set(
        plan.choir_participations.values_list("enrollment_id", flat=True)
    )
    PlanChoirParticipation.objects.bulk_create(
        [
            PlanChoirParticipation(plan=plan, enrollment_id=enrollment_id)
            for enrollment_id in selected_ids - existing_ids
        ]
    )


@transaction.atomic
def add_plan_song(*, plan, song, planned_key="", notes="", song_slot=None):
    WorshipPlan.objects.select_for_update().get(pk=plan.pk)
    last_position = plan.setlist_items.aggregate(last=Max("position"))["last"] or 0
    return PlanSong.objects.create(
        plan=plan,
        song=song,
        position=last_position + 1,
        song_slot=song_slot,
        planned_key=planned_key,
        notes=notes,
    )


@transaction.atomic
def move_plan_song(*, plan_song, direction):
    """Move a setlist item one position while preserving unique ordering."""
    locked_items = list(
        PlanSong.objects.select_for_update()
        .filter(plan=plan_song.plan)
        .order_by("position", "id")
    )
    current_index = next(
        (index for index, item in enumerate(locked_items) if item.pk == plan_song.pk),
        None,
    )
    if current_index is None:
        return False
    target_index = current_index - 1 if direction == "up" else current_index + 1
    if target_index < 0 or target_index >= len(locked_items):
        return False

    current = locked_items[current_index]
    target = locked_items[target_index]
    original_position = current.position
    temporary_position = locked_items[-1].position + 1
    current.position = temporary_position
    current.save(update_fields=("position",))
    target_position = target.position
    target.position = original_position
    target.save(update_fields=("position",))
    current.position = target_position
    current.save(update_fields=("position",))
    return True


@transaction.atomic
def remove_plan_song(*, plan_song):
    plan_id = plan_song.plan_id
    remaining = list(
        PlanSong.objects.select_for_update()
        .filter(plan_id=plan_id)
        .exclude(pk=plan_song.pk)
        .order_by("position", "id")
    )
    plan_song.delete()
    for position, item in enumerate(remaining, start=1):
        if item.position != position:
            item.position = position
            item.save(update_fields=("position",))


@transaction.atomic
def sync_song_assignments(*, plan_song, enrollments, actor, notes=""):
    PlanSong.objects.select_for_update().get(pk=plan_song.pk)
    selected_ids = {enrollment.pk for enrollment in enrollments}
    assignments = plan_song.assignments
    assignments.exclude(enrollment_id__in=selected_ids).delete()
    existing_ids = set(assignments.values_list("enrollment_id", flat=True))
    SongAssignment.objects.bulk_create(
        [
            SongAssignment(
                plan_song=plan_song,
                enrollment_id=enrollment_id,
                assigned_by=actor,
                notes=notes,
            )
            for enrollment_id in selected_ids - existing_ids
        ]
    )
    assignments.filter(enrollment_id__in=selected_ids).update(notes=notes)
    return assignments.filter(enrollment_id__in=selected_ids)


@transaction.atomic
def record_rehearsal_attendance(*, rehearsal, entries, actor):
    Rehearsal.objects.select_for_update().get(pk=rehearsal.pk)
    for entry in entries:
        RehearsalAttendance.objects.update_or_create(
            rehearsal=rehearsal,
            enrollment=entry["enrollment"],
            defaults={
                "status": entry["status"],
                "notes": entry["notes"],
                "recorded_by": actor,
            },
        )


def choir_leaders():
    """Linked members whose in-effect roles let them manage the choir."""
    return Member.objects.filter(
        user__in=users_with_permission("worship.manage_choir")
    ).order_by("last_name", "first_name")
