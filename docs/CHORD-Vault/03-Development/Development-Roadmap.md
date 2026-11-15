# Development Roadmap

1. **Phase 1: Environment and Django Foundation - Completed**
2. **Phase 2: Authentication and Role-Based Access Control - Completed**
3. **Phase 3: Core Church Administration - Reported completed and verified by
   the Phases 1-3 audit**
4. **Phase 4: Choir and Worship Management - Completed**
5. **Phase 5: Remaining Core Modules and System Integration - Completed**
   - Ministry structure and membership
   - Church-wide events, scheduling, registration, and attendance
   - Integration of events with rehearsals and worship plans
   - Confidential contribution recording and self-history
6. **Phase 6: Song Resources and Chord Sheet Integration - Completed**
7. **Phase 7: Dashboard, Reports, and UI/UX Refinement - In progress; paused
   after 7.3 milestone 6**
   - **Phase 7A: Multi-Tradition Support - Completed (2026-11-15).** Roman
     Catholic, Alliance, Iglesia Ni Cristo; Phase 8 inputs exposed via
     `services.slot_context()`. See [[../01-Project/Multi-Tradition-Support]].
   - Remaining Phase 7 screen groups resume next.
8. **Phase 8: Machine Learning Song Recommendation - Reserved; not started**
9. **Phase 9: Final Testing, Security, and Deployment - Planned**

Phase 8 is the only approved ML implementation phase. Until the user explicitly
authorizes it, CHORD must not add recommendation algorithms, ranking, TF-IDF,
cosine similarity, ML endpoints or interfaces, model evaluation, ML-only
tables, or ML-only dependencies. Existing structured song metadata and usage
history must remain intact for future integration.

Completed phase numbers remain unchanged. Work stops at every phase boundary
until the next phase is explicitly authorized.

See [[Task-Tracker]], [[Development-Log]], and
[[../01-Project/Project-Requirements]].
