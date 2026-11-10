# CHORD agent guidance

- Read `docs/CHORD-Vault/00-Home.md` and relevant linked notes before changes.
- Keep the vault aligned with actual code, commands, versions, tests, blockers,
  and decisions after each development task.
- Never place secrets or real passwords in code, Git, logs, or documentation.
- Preserve the custom user model and PostgreSQL configuration.
- Do not mark planned modules complete until their implementation is verified.
- Preserve the approved phase order: Phase 1 foundation, Phase 2 authentication
  and RBAC, Phase 3 core church administration, Phase 4 choir and worship,
  Phase 5 remaining core modules and integration, Phase 6 song resources and
  chord sheets, Phase 7 dashboards/reports/UI refinement, Phase 8 machine
  learning song recommendation, and Phase 9 final security/deployment.
- Machine learning is explicitly reserved for Phase 8. Before the user
  authorizes Phase 8, do not add recommendation algorithms, endpoints, UI,
  rankings, model-training code, ML tables, or ML-only dependencies.
- Preserve the structured song metadata and usage relationships needed by the
  future Phase 8 work without implementing recommendation behavior early.
- Phases 1-6, the Phase 7.2 design-system/application-shell milestone, and Phase
  7.3 dashboard, member-management, ministry, church-event, attendance, and
  giving milestones 1-4 are complete. Continue Phase 7 only through explicitly
  authorized screen groups; Phase 8 remains the only ML implementation phase.
- Use the exported `static/assets/CHORD.svg` as the visual reference while the
  Figma MCP read quota is unavailable. Inspect only the relevant screen region
  and never reproduce a screen as a single SVG image.
- Reuse the shared shell, design tokens, official branding partial, responsive
  navigation, and permission-backed links. Do not add design-only navigation
  for backend features that do not exist.
