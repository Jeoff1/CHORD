# Issue tracker: Local Markdown

Tickets for this repo live as Markdown files in `.scratch/`, committed to git.
They are **not** GitHub issues; do not use `gh issue` for them.

## Layout

- One feature or phase per directory: `.scratch/<feature-slug>/`
  (e.g. `.scratch/phase-7a/`).
- One file per ticket at `.scratch/<feature-slug>/issues/<NN>-<slug>.md`,
  numbered from `01`. Never a single combined tickets file.
- The spec for a feature lives in `.scratch/<feature-slug>/spec.md`, or in the
  vault (Phase 7A: `docs/CHORD-Vault/01-Project/Phase-7A-Spec.md`).

## Ticket file format

```markdown
# NN: Title

**What to build:** ...

**Blocked by:** NN, NN   (or "None (can start immediately)")

**Status:** ready-for-agent

- [ ] Acceptance criterion
```

- `**Status:**` uses the role strings in `triage-labels.md`, plus `done` once
  the work is implemented and committed.
- Comments and conversation history append to the bottom under `## Comments`.

## Conventions

- **List open tickets**: grep the `**Status:**` lines in
  `.scratch/<feature-slug>/issues/`; anything not `done` (or `wontfix`) is open.
- **Cross-check against git**: implementation commits name their ticket, e.g.
  `Add songbooks and metadata-only songs (ticket 05)`. Before reporting which
  tickets remain, run `git log --oneline | grep -i "ticket"` and reconcile; a
  ticket with a commit but a stale status must be verified, then marked.
- **Blocking**: a ticket is unblocked when every ticket in its `Blocked by`
  line has `**Status:** done`.
- **Close a ticket**: set `**Status:** done`, tick each satisfied acceptance
  criterion (`- [x]`), and note any unmet one. Commit the ticket file in the
  **same commit** as the implementation.

## When a skill says "publish to the issue tracker"

Create a new ticket file under `.scratch/<feature-slug>/issues/`, using the
next free number.

## When a skill says "fetch the relevant ticket"

Read the file at the referenced path. A bare reference like "ticket 03" means
`.scratch/<current-feature>/issues/03-*.md`; ask if more than one feature
directory matches.

## Pull requests as a triage surface

**PRs as a request surface: no.** _(`/triage` reads this flag.)_

## Wayfinding operations

Used by `/wayfinder`. The **map** is a file with one **child** file per ticket.

- **Map**: `.scratch/<effort>/map.md` (Notes / Decisions-so-far / Fog).
- **Child ticket**: `.scratch/<effort>/issues/NN-<slug>.md` with a `Type:` line
  (`research`/`prototype`/`grilling`/`task`) and a `Status:` line
  (`claimed`/`resolved`).
- **Blocking**: a `Blocked by: NN, NN` line; unblocked when every listed file is
  `resolved`.
- **Frontier**: the first open, unblocked, unclaimed file by number.
- **Claim**: set `Status: claimed` and save before any work.
- **Resolve**: append the answer under `## Answer`, set `Status: resolved`, then
  append a context pointer to the map's Decisions-so-far.

## Remote

The code is hosted at **`Jeoff1/CHORD`** (git remote `CHORD-Jop`, not
`origin`), but tickets are not filed there.
