# OpsKnowledge Brand Guide

Authoritative visual, typographic, and voice reference for OpsKnowledge. Aligns with `AGENTS.md` (normative) and `RAG_ROADMAP.md` (product boundary); does not contradict them. Future designers and developers use this guide to keep the interface consistent across surfaces.

## Quick path

1. Read [Principles](#principles) to understand the brand hierarchy.
2. Use the [Wordmark](#wordmark) and [Palettes](#palettes) tables when picking color or type roles.
3. Apply [Voice](#voice) and [Accessibility gates](#accessibility--usage-gates) before shipping copy or components.
4. Run the [Implementation checklist](#implementation-checklist) before merging a UI change.

## Principles

| Priority | Principle | What it means in practice |
|----------|-----------|---------------------------|
| 1 | Clarity | Every screen is readable at a glance; hierarchy comes from type and spacing, not from boxes or color blocks. |
| 2 | Confidence | Restraint signals trust: no decorative illustration, no noise, no visual filler. |
| 3 | Approachability | Warm, editorial, human, never sterile or generic SaaS. |

**Personality:** contemporary editorial, sober, minimal, corporate, warm. Not futuristic, decorative, playful, or generic SaaS.

## Wordmark

- **Name:** OpsKnowledge (one word, capital K).
- **Treatment:** typography only. No logomark, no symbol, no monogram.
- **Typeface:** Source Sans 3, Medium weight, with subtle optical spacing (tracking slightly opened; figures aligned to baseline; uniform stroke contrast).
- **Color:** ink blue `#24445C` on light surfaces; primary text `#F1EFE9` on dark surfaces.
- **Clear space:** at least the cap height of the "K" on every side.
- **Forbidden:** stretching, recoloring with non-brand hues, adding shadows, outlines, gradients, rotating, pairing with custom symbols, or substituting alternate typefaces.

## Palettes

### Light palette (primary)

| Role | Token | Hex | Use for |
|------|-------|-----|---------|
| Brand | `--ink-blue` | `#24445C` | Wordmark, primary action emphasis, links, key data |
| Surface base | `--ivory` | `#F7F5F0` | App background |
| Surface elevated | `--ivory-light` | `#FCFBF8` | Cards, panels, surfaces above the base |
| Text primary | `--charcoal` | `#242321` | Headings, body copy |
| Text secondary | `--warm-gray` | `#65615B` | Captions, helper text, metadata |
| Border | `--warm-border` | `#DDD9D1` | Hairlines, dividers, input borders |

### Dark palette (supported alternative)

| Role | Token | Hex | Use for |
|------|-------|-----|---------|
| Background | `--ink-black` | `#171918` | Page background |
| Surface | `--ink-surface` | `#1E211F` | Cards, panels |
| Surface elevated | `--ink-elevated` | `#252925` | Modals, popovers |
| Text primary | `--ivory-text` | `#F1EFE9` | Headings, body copy |
| Text secondary | `--stone` | `#B8B4AB` | Captions, helper text |
| Border | `--ink-border` | `#373B37` | Hairlines, dividers |
| Interactive | `--ink-blue-bright` | `#7FA6BE` | Links, focus rings, primary actions |
| Reserved brand | `--ink-blue` | `#24445C` | Non-critical surfaces, details, and accents only; never primary text |

**Rule:** do not apply dark and light themes to the same surface. Light remains the default expression; dark is a fully supported user-selectable theme. Both themes require contrast and accessibility validation before release.

## Typography

Two free, open-source families. Source Sans 3 does the work; Source Serif 4 is a quiet accent.

| Role | Family | Weight | Tracking | Notes |
|------|--------|--------|----------|-------|
| Display, headings, body, UI | Source Sans 3 | 400, 500, 600 | Optical; normal for body, slightly tight (-0.01em) for display | Default for almost every text element. |
| Accent: major section openers, long-form intros | Source Serif 4 | 400, 500 | Normal | One use per surface; never inside dense UI or tables. |

**Type scale (Source Sans 3):**

| Step | Size | Line height | Use for |
|------|------|-------------|---------|
| Display | 40 / 48 | 1.1 | Hero, marketing |
| H1 | 32 | 1.2 | Page title |
| H2 | 24 | 1.3 | Section title |
| H3 | 20 | 1.3 | Subsection title |
| Body L | 18 | 1.5 | Reading copy |
| Body | 16 | 1.5 | Default body |
| Caption | 14 | 1.4 | Helper, metadata |
| Micro | 12 | 1.4 | Legal, tags |

**Hierarchy rule:** use a scale ratio of at least 1.25 between primary hierarchy levels (for example, H1 to H2). Intermediate text roles may use smaller increments when their function remains unambiguous. Weight contrast (500 vs 600) may reinforce hierarchy but never replaces scale.

## Spacing and layout

- **Base unit:** 4px. Use 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96.
- **Reading lines:** 65 to 75 characters per line for long-form text.
- **Section padding:** minimum 64px vertical on desktop; scale down to 48px on tablet and 32px on mobile.
- **Container widths:** narrow 720px (articles), standard 1024px (dashboards), wide 1280px (lists, tables).
- **Hierarchy through spacing and type:** prefer whitespace and type over extra cards, dividers, or fills. Most groupings do not need a container.
- **Density:** spacious and editorial by default. Denser treatment is acceptable only where operationally necessary (tables, logs, dense data) and must remain legible at the base body size.
- **Mobile navigation:** a compact left-side menu may contain the wordmark inside the drawer instead of keeping it visible in the closed header. The primary composer may remain fixed near the bottom in both initial and active chat states when safe areas, virtual keyboard behavior, notices, and content clearance are preserved.

## Shape

Rounded, but restrained. Larger radii are reserved for conversational surfaces where they improve continuity and touch affordance. Pills remain reserved for semantic tags and filters.

| Surface | Radius |
|---------|--------|
| Compact controls (chips, small toggles) | 6px |
| Buttons, inputs, menu items | 8px |
| Panels, cards, modals | 12px |
| Chat composers and conversational input surfaces | 16px |
| Pills, tags, filters | full (999px) |

Borders are 1px in `--warm-border` (or `--ink-border` in dark). Drop shadows are rare; if used, keep them low-elevation and warm-tinted (never pure black).

## Icons

- Thin, technical, line-based.
- Stroke: ~1.5px.
- Joins and caps: rounded.
- Default size: 18 to 20px.
- Pair with a label whenever the meaning is not universal (for example, do not rely on a bell icon alone to mean "alerts").
- A circular icon-only send control is an approved exception for chat composers. It requires a clear paper-plane/send glyph, an accessible name, visible focus, tooltip, and a minimum 44x44px target. During generation, it changes to an equally explicit stop control.
- Single accent color: ink blue on light, `--ink-blue-bright` on dark. Never multicolor.

## Motion

- **Duration:** 220 to 320ms for fades and short translations.
- **Easing:** ease-out with exponential feel; no bounce, no elastic, no spring.
- **Scope:** opacity and transform only. Do not animate layout properties (width, height, top, left).
- **Feedback:** every interactive element returns a state change in under 100ms; if a longer operation follows, show a quiet progress affordance.
- **Reduced motion:** respect `prefers-reduced-motion: reduce`; fall back to opacity-only or no animation.

## Voice

**Tone:** formal and neutral, concise by default, discreet first person. Avoid direct address ("you", "tu", "usted", "ustedes") where a natural neutral construction exists; prefer impersonal phrasing. Screen-specific, explicitly approved formal prompts may use implied formal address sparingly when no neutral alternative reads naturally. Such exceptions are recorded per surface and require explicit approval; they do not generalize. Retain precise technical terminology. No humor, no anthropomorphism, no artificial enthusiasm.

**Approved exceptions:**

- Main chat initial heading `¿Qué desea consultar hoy?` (approved during the main-chat OpenDesign handoff). This is the sole approved exception on the main chat screen; no other direct-address copy is permitted there without equivalent approval.

### Voice do / don't

| Do | Don't |
|----|-------|
| "Citation required to confirm scope." | "We need a citation real quick!" |
| "Evidence was not found in the approved sources." | "Unfortunately, we couldn't find anything." |
| "First-person note: this answer is provisional." | "I think this might be right." |
| "Recommended next step: consult a human expert." | "You should totally ask a human for help." |
| "Generation provider is unavailable; no answer was persisted." | "Oops, our AI is down. Try again later." |

### Abstention wording (template)

> "I could not verify this information in the approved sources. Consulting a specialist is recommended."

- Use this wording for missing evidence, out-of-scope questions, source contradictions, and unsupported claims.
- Use a separate, provider-focused message when the generation or embedding provider is unavailable (timeout, rate limit, outage): state that the provider is unavailable, recommend a human expert, and confirm that no answer was persisted. Distinguish the two clearly; do not conflate missing evidence with provider failure.

### Safety-aligned copy rules

- Every technical claim references a citation to a current approved entry.
- Unsupported, out-of-scope, or contradictory cases abstain and recommend a human expert.
- Conversation history, glossary entries, support history, and model knowledge are never answer evidence; never present them as such.
- The prototype demo surface shows explicit demo warnings and a visible non-corporate demo policy.

## Accessibility and usage gates

| Gate | Threshold | How to verify |
|------|-----------|---------------|
| Contrast, normal text | WCAG 2.2 AA: 4.5:1 | Run a contrast checker on every text/background pair before release. |
| Contrast, large text | 3:1 | Same as above. |
| Non-text contrast (icons, focus rings, borders) | 3:1 against adjacent surface | Same as above. |
| Focus visibility | Visible 2px focus ring on every interactive element | Keyboard-only walkthrough. |
| Hit target | Minimum 44x44 CSS pixels for any interactive element | Automated axe scan. |
| Reduced motion | All motion respects `prefers-reduced-motion: reduce` | Manual toggle test. |
| Language attribute | `lang` attribute matches active locale on `<html>` and per-block | HTML validator. |
| Keyboard | Every action is reachable and operable by keyboard alone | Keyboard walkthrough. |

**Important:** include contrast validation as an implementation gate. Do not assume every proposed color pair has already been formally audited; verify at design and PR time.

## Anti-patterns

Avoid these in any surface:

- Decorative illustrations, mascots, stock photography.
- Gradient text, glassmorphism used as decoration, side-stripe accents.
- Identical "icon + heading + paragraph" card grids repeated without variation.
- Modal as the first interaction pattern; exhaust inline and progressive alternatives first.
- Generic SaaS chrome: rounded everything, multi-color gradients, animated blobs.
- Direct address to the user in copy ("you", "tu", "we recommend you...") where a natural neutral construction exists. Screen-specific, explicitly approved formal prompts that use implied formal address sparingly are not anti-patterns; see Voice for the exception process.
- Humor, emoji, exclamation marks in product copy.
- Em dashes (use commas, colons, semicolons, periods, or parentheses instead).
- Pure black `#000000` or pure white `#FFFFFF` as primary surfaces or text.

## Implementation checklist

Before merging a UI change:

- [ ] Wordmark is typography only, in Source Sans 3 Medium, in a brand color.
- [ ] Light is the default and dark is fully supported; both themes are contrast-checked across every implemented state.
- [ ] Source Sans 3 is used for UI and body; Source Serif 4 only for one major section opener per surface.
- [ ] Type scale follows the table; primary hierarchy levels differ by at least 1.25x.
- [ ] Reading lines are 65 to 75 characters where applicable.
- [ ] Radii match the shape table; 16px is limited to chat composers and conversational input surfaces; pills are reserved for tags and filters.
- [ ] Icons are 1.5px stroke, 18 to 20px, paired with a label when meaning is not universal.
- [ ] Icon-only send and stop controls include an accessible name, tooltip, visible focus, and a minimum 44x44px target.
- [ ] Motion is 220 to 320ms, opacity/transform only, and respects `prefers-reduced-motion`.
- [ ] Voice follows the do/don't table; direct address avoided where a natural neutral construction exists; approved exceptions documented per surface; no humor, no em dashes.
- [ ] Abstention copy uses the template; provider-unavailable copy is distinct from missing-evidence copy.
- [ ] Contrast and focus gates pass automated checks and a keyboard walkthrough.
- [ ] No decorative illustration, gradient text, glassmorphism, or side-stripe accents.
- [ ] AGENTS.md safety language is preserved on every screen that exposes answers, citations, or abstention.

## Related documents

- `AGENTS.md`: normative contributor contract and cross-phase safety invariants.
- `RAG_ROADMAP.md`: product boundary, phases, and guiding principles.
- `docs/architecture/platform-architecture.md`: logical and physical architecture, flows, traceability.
