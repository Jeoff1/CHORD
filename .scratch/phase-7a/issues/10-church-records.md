# 10: Church Records module

**What to build:** Authorized users create, edit, search and filter Church Records (baptism, confirmation, marriage, dedication, funeral and so on), with record types that depend on the active Tradition. Records link to a member or a free-text name and keep an audit trail.

**Blocked by:** 02, 03

**Status:** ready-for-agent

- [ ] New records app with Church Record Type (per Tradition) and Church Record
- [ ] Each record has a member link or free-text name, officiant, place, date and notes
- [ ] A dedicated permission keeps records confidential to authorized roles
- [ ] Audit events mirror the existing member and contribution audits
- [ ] Search and filter by type and date
- [ ] The module respects module toggles
- [ ] HTTP-client tests cover CRUD, confidentiality and the audit trail
