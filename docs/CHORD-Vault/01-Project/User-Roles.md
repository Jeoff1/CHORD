# User Roles

Phase 2 seeds six roles. Users may have multiple roles when their real
responsibilities require it.

| Role | Responsibility boundary |
| --- | --- |
| Church Administrator | Manages accounts, role assignments, and member records; receives sensitive member access but no automatic future-module access |
| Ministry Leader | Future ministry membership, activities, schedules, and assignments |
| Worship Leader | Future songs, recommendations, worship plans, and setlists |
| Choir Leader | Future choir membership, rehearsals, assignments, and preparation |
| Choir Member | Future assigned songs, rehearsals, announcements, and authorized resources |
| Church Member | Future permitted church information and own applicable records |

Church Administrator currently has scoped account and member-management
permissions. Other roles receive permissions only when required by an
implemented workflow. A linked account may view its own member record without a
broad directory permission. Django superuser remains a separate emergency
framework capability.

Role assignment is not the same as choir participation or future object-level
membership. See [[../03-Modules/Authentication]] and
[[../02-Architecture/Architecture-Decisions]].
