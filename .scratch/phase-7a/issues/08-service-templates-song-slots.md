# 08: Service Templates and Song Slots

**What to build:** A worship leader can create a worship plan from a Service Template. Its setlist entries fill named Song Slots (e.g. Entrance, Offertory, Communion, Recessional for Mass; generic slots for free-form traditions). Plans without a template still work.

**Blocked by:** 01, 05

**Status:** done

- [x] Each Tradition preset has Service Templates with ordered Song Slots
- [x] WorshipPlan gains an optional Service Template, and PlanSong gains an optional Song Slot
- [x] Position ordering stays authoritative
- [x] Creating a plan from a template pre-builds its slots (derived from the template by `WorshipPlan.slot_outline()` and shown as open slots on plan detail, not stored as empty setlist rows)
- [x] Tests cover plans with and without a template
