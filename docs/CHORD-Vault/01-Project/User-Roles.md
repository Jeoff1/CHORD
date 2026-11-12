# User Roles

CHORD seeds six common roles plus each Tradition's own roles. A Tradition
role grants access only while its Tradition is active (see
[[../03-Modules/Church-Profile-Traditions]]). Users may have multiple roles
when their real responsibilities require it.

All roles are defined as data in the role catalogue
(`apps/traditions/roles.py`) and synchronized after every migrate. Code never
checks a role code: access is checked through Django permissions, and "who
holds a capability" is answered by `services.users_with_permission(perm)`
(e.g. the choir-leader lists use `worship.manage_choir`, so a Parish Priest or
Church Administrator also appears there).

| Tradition | Preset roles (permission set reused) |
| --- | --- |
| Alliance | Senior Pastor (Church Administrator), Head Deacon (Ministry Leader) |
| Iglesia Ni Cristo | Minister (Church Administrator), Head Deacon (Ministry Leader) |
| Roman Catholic | Parish Priest (Church Administrator), Music Director (Worship Leader) |

Common roles:

| Role | Responsibility boundary |
| --- | --- |
| Church Administrator | Manages accounts, members, ministries, events/attendance, choir/worship, funds, and confidential contributions |
| Ministry Leader | Manages membership and events only for ministries where the linked member is an active leader |
| Worship Leader | Manages songs, authorized resources, worship plans, setlists, choir participation, and song assignments |
| Choir Leader | Manages choir enrollment, rehearsals, attendance, announcements, and choir song assignments |
| Choir Member | Views rehearsals, applicable announcements, authorized song resources, participating plans, and own song assignments |
| Church Member | Views eligible ministries/events, registers for events, and views giving linked to their member record |

Role mappings are authoritative and synchronized after migrations. Worship and
Choir Leaders have separate responsibility boundaries; Choir Members receive
participant views only. All six roles may view permitted church events and
their own linked giving history; event visibility further depends on active
ministry membership. A linked account may view its own member record without a
broad directory permission. Django superuser remains a separate emergency
framework capability.

Role assignment is not the same as choir participation. `ChoirEnrollment`
connects an existing member record to the choir domain, while a Choir Member
role controls application access.

Likewise, a Ministry Leader role alone does not grant object access.
`MinistryMembership(role=leader, status=active)` must connect that user's member
record to the ministry being managed.

See [[../03-Modules/Authentication]],
[[../03-Modules/Choir-Worship-Management]], and
[[../02-Architecture/Architecture-Decisions]].
