# 10: Church Records module

**What to build:** Authorized users create, edit, search and filter Church Records (baptism, confirmation, marriage, dedication, funeral and so on), with record types that depend on the active Tradition. Records link to a member or a free-text name and keep an audit trail.

**Blocked by:** 02, 03

**Status:** done

- [x] New records app with Church Record Type (per Tradition) and Church Record
- [x] Each record has a member link or free-text name, officiant, place, date and notes
- [x] A dedicated permission keeps records confidential to authorized roles
- [x] Audit events mirror the existing member and contribution audits
- [x] Search and filter by type and date
- [x] The module respects module toggles
- [x] HTTP-client tests cover CRUD, confidentiality and the audit trail
