# Giving

Status: **Completed - Phase 5 (2026-11-09)**

## Implemented

- Active/inactive giving funds
- Identified or anonymous contributions with positive decimal amount, date,
  method, optional reference, and internal notes
- Church Administrator-only fund and contribution management
- Audit entries containing actor, action, timestamp, and changed field names
  without copied confidential values
- Member self-history limited to contributions connected to that user's
  one-to-one member record
- Database checks for positive amounts and consistent anonymous/member identity

There is no public deletion workflow. Anonymous contributions are deliberately
not recoverable through member self-history. Aggregate giving dashboards and
reports belong to Phase 7.

See [[../02-Architecture/Database-Design]], [[../03-Development/Known-Issues]],
and [[../04-Testing/Phase-5-Test-Results]].
