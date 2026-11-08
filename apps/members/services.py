from .models import MemberAuditEvent


def record_member_event(*, member, actor, action, fields_changed=()):
    """Record field names only; never duplicate sensitive values in the audit log."""
    return MemberAuditEvent.objects.create(
        member=member,
        actor=actor if actor.is_authenticated else None,
        action=action,
        fields_changed=sorted(fields_changed),
    )
