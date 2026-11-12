# 02: Tradition terminology and module toggles

**What to build:** Navigation and headings use the active Tradition's terms (e.g. Mass, Worship Service, Pagsamba). A church administrator can toggle modules off. Disabled modules disappear from navigation, and their URLs return 404.

**Blocked by:** 01

**Status:** done

- [x] Terminology comes from the tradition-config service through one context processor
- [x] Each Tradition preset ships default module toggles
- [x] Disabled-module URLs return 404 through one shared mechanism
- [x] Permission checks stay authoritative regardless of toggles
- [x] HTTP-client tests cover switching Tradition and toggling a module
