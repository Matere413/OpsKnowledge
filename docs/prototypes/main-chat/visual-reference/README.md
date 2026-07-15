# Main chat visual reference

Visual design reference only. This folder holds generated visual output from an
OpenDesign exploration of the OpsKnowledge main chat surface.

## What this is

- A self-contained `index.html` snapshot used to evaluate the look, composition,
  and feel of the main chat UI.
- `brand-spec.md` documents the visual tokens and posture used by the generated
  snapshot. The authoritative brand source remains `brand-guide.md`.

## What this is NOT

This artifact is **not** any of the following:

- A demo or runnable prototype.
- A runtime implementation of the OpsKnowledge platform.
- Security evidence or proof of any safety, screening, provider, or session
  guarantee.
- An accessibility certification. Contrast and markup here are illustrative, not
  audited.
- A spec. The generated interactions and states are illustrative and must not be
  reused as production logic.

## Data handling warning

Never enter real, corporate, personal, sensitive, or confidential data into the
local HTML. It is a static visual snapshot with no backend, no screening, and no
safe persistence. Treat any input field as purely cosmetic.

## Known gaps

The snapshot does not implement and must not be assumed to provide:

- Query language filtering or screening before model processing.
- Provider failure abstention, bounded retry, or outage handling.
- Session expiration, retention, or query-durability transaction behavior.
- Authorization, audit logging, or sensitive-data blocking.
- Any of the cross-phase safety invariants defined in `AGENTS.md` and
  `RAG_ROADMAP.md`.

## Authority

`AGENTS.md` (repository root) and `brand-guide.md` remain the authoritative
contracts for architecture, safety, and brand. Where this visual reference
disagrees with them, they win and this artifact is wrong.