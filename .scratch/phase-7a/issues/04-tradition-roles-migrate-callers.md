# 04: Tradition roles, migrate callers and contract

**What to build:** Every place that checks a hardcoded role code now checks permissions or resolves roles through the tradition-config service, so CHORD behaves correctly under any Tradition's roles. The old fixed-code dependencies are removed.

**Blocked by:** 03

**Status:** done

- [ ] No references to the six fixed role codes remain outside migrations
- [ ] Access tests pass under each of the three Traditions
- [ ] The vault User-Roles note is updated
