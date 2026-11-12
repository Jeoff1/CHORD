# 08: Service Templates and Song Slots

**What to build:** A worship leader can create a worship plan from a Service Template. Its setlist entries fill named Song Slots (e.g. Entrance, Offertory, Communion, Recessional for Mass; generic slots for free-form traditions). Plans without a template still work.

**Blocked by:** 01, 05

**Status:** ready-for-agent

- [ ] Each Tradition preset has Service Templates with ordered Song Slots
- [ ] WorshipPlan gains an optional Service Template, and PlanSong gains an optional Song Slot
- [ ] Position ordering stays authoritative
- [ ] Creating a plan from a template pre-builds its slots
- [ ] Tests cover plans with and without a template
