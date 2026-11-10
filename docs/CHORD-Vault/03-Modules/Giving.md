# Giving

Status: **Core completed in Phase 5; Phase 7.3 UI refined (2026-11-10)**

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

## Phase 7.3 interface

- Confidential administrator ledger with donor/fund/reference search and fund,
  method, and date-range filters
- Real filtered contribution total, identified/anonymous counts, and top-fund
  summary derived from the authorized queryset
- Fund-category directory with active status, record counts, and recorded totals
- Refined contribution and fund forms that preserve existing validation and
  atomic audit services
- Recorded-by, entered-at, method, reference, donor identity, and fund metadata
  shown only on the administrator ledger
- Private member history with member-scoped date/fund filters and totals; no
  other donor, notes, reference, or audit metadata enters that context
- Responsive tables, forms, summary cards, empty states, and confidentiality
  guidance using shared Phase 7 components

Online collection, payment gateways, reconciliation state, tax receipts,
giving reports, and ledger export remain unimplemented. The model's existing
`online` method means an external contribution was manually recorded; CHORD
does not process that payment.

See [[../02-Architecture/Database-Design]], [[../03-Development/Known-Issues]],
and [[../04-Testing/Phase-5-Test-Results]].
