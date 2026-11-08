# User Roles

CHORD seeds six roles. Users may have multiple roles when their real
responsibilities require it.

| Role | Responsibility boundary |
| --- | --- |
| Church Administrator | Manages accounts, member records, and implemented choir/worship workflows; receives no automatic future-module access |
| Ministry Leader | Future ministry membership, activities, schedules, and assignments |
| Worship Leader | Manages songs, authorized resources, worship plans, setlists, choir participation, and song assignments |
| Choir Leader | Manages choir enrollment, rehearsals, attendance, announcements, and choir song assignments |
| Choir Member | Views rehearsals, applicable announcements, authorized song resources, participating plans, and own song assignments |
| Church Member | Uses permitted member-facing CHORD features |

Role mappings are authoritative and synchronized after migrations. Worship and
Choir Leaders have separate responsibility boundaries; Choir Members receive
participant views only. A linked account may view its own member record without
a broad directory permission. Django superuser remains a separate emergency
framework capability.

Role assignment is not the same as choir participation. `ChoirEnrollment`
connects an existing member record to the choir domain, while a Choir Member
role controls application access.

See [[../03-Modules/Authentication]],
[[../03-Modules/Choir-Worship-Management]], and
[[../02-Architecture/Architecture-Decisions]].
