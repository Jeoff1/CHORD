# CHORD Vault

CHORD's source-of-truth development notes.

- [[01-Project/Project-Overview|Project Overview]]
- [[01-Project/Project-Requirements|Project Requirements]]
- [[01-Project/Technology-Stack|Technology Stack]]
- [[01-Project/User-Roles|User Roles]]
- [[01-Project/Multi-Tradition-Support|Multi-Tradition Support]]
- [[01-Project/Phase-7A-Spec|Phase 7A Spec]]
- [[02-Architecture/Environment-Setup|Environment Setup]]
- [[02-Architecture/Database-Configuration|Database Configuration]]
- [[02-Architecture/Project-Structure|Project Structure]]
- [[02-Architecture/Database-Design|Database Design]]
- [[02-Architecture/Architecture-Decisions|Architecture Decisions]]
- [[03-Modules/Authentication|Authentication and RBAC]]
- [[03-Modules/Member-Management|Member Management]]
- [[03-Modules/Choir-Worship-Management|Choir and Worship Management]]
- [[03-Modules/Song-Resources-Chord-Sheets|Song Resources and Chord Sheets]]
- [[03-Modules/Ministry-Management|Ministry Management]]
- [[03-Modules/Events-Attendance|Events and Attendance]]
- [[03-Modules/Giving|Giving]]
- [[03-Modules/Church-Profile-Traditions|Church Profile and Traditions]]
- [[03-Development/Development-Roadmap|Development Roadmap]]
- [[03-Development/Phase-7-Figma-Design-Audit|Phase 7 Figma Design Audit]]
- [[03-Development/Design-System|Design System]]
- [[03-Development/Branding-and-Assets|Branding and Assets]]
- [[03-Development/Screen-Implementation-Tracker|Screen Implementation Tracker]]
- [[03-Development/Design-Change-Log|Design Change Log]]
- [[03-Development/New-Church-Setup|New Church Setup]]
- [[03-Development/Task-Tracker|Task Tracker]]
- [[03-Development/Development-Log|Development Log]]
- [[03-Development/Known-Issues|Known Issues]]
- [[03-Development/Refactoring-Log|Refactoring Log]]
- [[04-Testing/Environment-Verification|Environment Verification]]
- [[04-Testing/Phase-2-Test-Results|Phase 2 Test Results]]
- [[04-Testing/Phase-3-Test-Results|Phase 3 Test Results]]
- [[04-Testing/Phases-1-3-QA-Audit|Phases 1-3 QA Audit]]
- [[04-Testing/Phase-4-Test-Results|Phase 4 Test Results]]
- [[04-Testing/Phase-5-Test-Results|Phase 5 Test Results]]
- [[04-Testing/Phase-6-Test-Results|Phase 6 Test Results]]
- [[04-Testing/Phase-7-Test-Results|Phase 7 Test Results]]

Current status: **PHASE 7.3 MILESTONE 6 COMPLETE.** Worship-plan directories,
service details, preparation statuses, linked events, ordered setlists, choir
participation, song assignments, forms, Spotify links, and protected resources
now use the Phase 7.2 shell. Existing object access, transactional ordering,
participant synchronization, and resource security remain authoritative. All
149 tests, PostgreSQL test-database execution, migration consistency, Django
checks, Ruff lint, and Ruff formatting passed on 2026-11-10. Remaining screen
groups and reports are separate milestones. **Phase 7A Multi-Tradition Support** is complete (2026-11-15). Next: remaining
Phase 7 screen groups. Machine learning is reserved for
Phase 8 and is neither implemented nor in progress.
