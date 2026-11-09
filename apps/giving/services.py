from django.db import transaction

from .models import Contribution, ContributionAuditEvent


@transaction.atomic
def record_contribution(*, form, actor):
    contribution = form.save(commit=False)
    contribution.recorded_by = actor
    contribution.save()
    form.save_m2m()
    ContributionAuditEvent.objects.create(
        contribution=contribution,
        actor=actor,
        action=ContributionAuditEvent.Action.CREATED,
        fields_changed=form.changed_data,
    )
    return contribution


@transaction.atomic
def update_contribution(*, form, actor):
    contribution = form.save()
    ContributionAuditEvent.objects.create(
        contribution=contribution,
        actor=actor,
        action=ContributionAuditEvent.Action.UPDATED,
        fields_changed=form.changed_data,
    )
    return contribution


def contributions_for_member_user(user):
    if not user.is_authenticated:
        return Contribution.objects.none()
    return Contribution.objects.filter(member__user=user).select_related("fund")
