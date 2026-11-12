# 06: Controlled Themes for songs

**What to build:** Themes become a controlled list: a shared common list plus each Tradition's own Themes. Songs are tagged from this list. Existing free-string song themes migrate where they match, and unmatched strings are reported for manual tagging.

**Blocked by:** 01

**Status:** ready-for-agent

- [ ] Theme model, either common or tradition-scoped
- [ ] Song themes become a relation to Theme
- [ ] The migration maps matching legacy strings, and a management command reports unmatched ones
- [ ] Song forms offer common Themes plus the active Tradition's Themes
- [ ] Tests cover migration matching and theme options per Tradition
