from apps.traditions.services import get_active_tradition

from .models import ChurchRecordAuditEvent, ChurchRecordType


def available_record_types(tradition=None):
    """Church Record Types the active Tradition offers."""
    return ChurchRecordType.objects.filter(
        tradition=tradition or get_active_tradition()
    )


def record_church_record_event(*, record, actor, action, fields_changed=()):
    """Record field names only; never duplicate confidential values in the log."""
    return ChurchRecordAuditEvent.objects.create(
        record=record,
        actor=actor if actor.is_authenticated else None,
        action=action,
        fields_changed=sorted(fields_changed),
    )
