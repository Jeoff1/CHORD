# 03: Tradition roles, expand

**What to build:** Roles can belong to a Tradition or be common. The fixed role-code choices are removed. The existing six roles are migrated so every user keeps the same access. Each preset defines its own roles (e.g. Parish Priest, Senior Pastor, Minister, Head Deacon), mapped to Django permissions.

**Blocked by:** 01

**Status:** done

- [ ] Role gains an optional Tradition, and codes are no longer limited to fixed choices
- [ ] A data migration preserves every existing user's effective permissions
- [ ] Roles of an inactive Tradition grant no access
- [ ] Administrators can assign Tradition roles to users
- [ ] The old role-code helpers still work (ticket 04 removes them)
- [ ] Tests prove access is unchanged after the migration
