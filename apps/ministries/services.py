from .models import MinistryMembership


def led_ministry_ids(user):
    """Return ministry IDs the linked account actively leads."""
    if not user.is_authenticated or not user.is_active:
        return MinistryMembership.objects.none().values_list("ministry_id", flat=True)
    return MinistryMembership.objects.filter(
        member__user=user,
        role=MinistryMembership.Role.LEADER,
        status=MinistryMembership.Status.ACTIVE,
    ).values_list("ministry_id", flat=True)


def can_manage_ministry(user, ministry):
    if user.has_perm("ministries.manage_ministries"):
        return True
    return (
        user.has_perm("ministries.manage_assigned_ministries")
        and MinistryMembership.objects.filter(
            ministry=ministry,
            member__user=user,
            role=MinistryMembership.Role.LEADER,
            status=MinistryMembership.Status.ACTIVE,
        ).exists()
    )
