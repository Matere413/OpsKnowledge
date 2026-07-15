# OpsKnowledge Main Chat Screen — OpenDesign Handoff Prompt

A self-contained design specification for the OpsKnowledge main chat screen, ready to paste into OpenDesign. Read this file together with its two companion assets:

- `../../brand/brand-guide.md` — authoritative visual, typographic, and voice reference. This prompt never overrides it; it only applies it.
- `assets/ParticleSphere.tsx` — standalone React + Three.js reference component for the signature particle sphere. Provide it to OpenDesign as an attached asset.

> **MVP UI language:** Spanish (formal, neutral). All visible UI copy in this prototype stays in Spanish. Technical artifacts, identifiers, and comments remain in English.

---

## 1. Product context (read first)

OpsKnowledge is an operational knowledge assistant. It answers questions using ONLY current approved source documents (runbooks, ADRs, policies). It never invents evidence. When evidence is missing, out of scope, contradictory, or the generation provider is unavailable, it abstains and recommends a human expert.

The main chat screen is the single primary surface. It is editorial, spacious, warm, and restrained. It is NOT a generic SaaS chat app and NOT a consumer AI toy.

**Demo surface policy (mandatory, from `AGENTS.md`):** this prototype is a public-OpenAI demo. It accepts free-text questions using ONLY synthetic manifest documents and fragments. The UI MUST show an explicit demo warning and a visible non-corporate demo policy at all times. The architecture does NOT claim that arbitrary user-entered question text is provably synthetic. A high-confidence sensitive screen runs before any embedding or generation; rejected payloads do not persist. The demo is visibly non-corporate and cannot be wired outside the `development` profile. Corporate users, corporate data, and the corporate MVP free-text path MUST NOT use this demo mode.

**What this screen does:**

- Accept one free-text question at a time in a multiline composer.
- Detect the query language automatically (no language selector control).
- Retrieve evidence from approved sources, filtered to the query language.
- Answer with inline numbered citations and a collapsible sources disclosure under each answer.
- Abstain explicitly when evidence is missing, out of scope, contradictory, or the provider is unavailable.
- Block sensitive payloads before any model processing or persistence.
- Keep conversation context only within the active session. No cross-session history.
- Persist question, outcome, answer, citations, and analytical record in ONE transaction after generation; if persistence fails, respond `unavailable` and expose no answer.

**What this screen deliberately does NOT do (do not invent any of these):**

- Document upload, attachment, file ingestion, or source management UI.
- Persistent chat history across sessions or a history list in the sidebar.
- A source library, model selector, language selector, or reranking control.
- An admin dashboard. Admin access, if present, is conditionally nested inside Profile and never a top-level surface.
- Gradients (of any kind), glassmorphism, blur decoration, illustrations, mascots, avatars, stock photography, floating cards, side-stripe accents.
- Generic "purple/blue AI" styling, animated blobs, neon, or dark-by-default theming.
- Letter-by-letter human-typing simulation for generation. Generation is explicit and calm (see §6).
- Anthropomorphism, humor, exclamation marks, artificial enthusiasm, or direct address other than the approved heading exception in §11.

---

## 2. Theme, register, and aesthetic commitment

- **Light theme is primary.** Default the screen to light. Dark theme is a future opt-in per surface and is NOT designed here beyond the ParticleSphere color tokens and the abstract state tokens listed in §9.
- **Register:** product (design serves the product, not brand marketing).
- **Aesthetic:** contemporary editorial, sober, minimal, corporate, warm. Generous whitespace. Hierarchy through type and spacing, not boxes. Most groupings do not need a container.

Apply the cognitive load rules from `brand-guide.md`: lead with the answer, progressive disclosure, one clear idea per screen region, recognition over recall. The center composition is a single staged idea; everything else recedes.

**Bans (match-and-refuse):** side-stripe borders, gradient text, glassmorphism as decoration, the hero-metric template, identical icon+heading+paragraph card grids, modal as first thought, pure black `#000` or pure white `#fff` as primary surfaces/text, em dashes in copy (use commas, colons, semicolons, periods, parentheses).

---

## 3. Layout — three breakpoints

Use the brand container widths and section padding. Base unit 4px; use 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96.

### 3.1 Desktop (≥1024px)

```
+--------------------------------------------------------------+
| [sidebar rail 64px] | [main area, standard 1024px container]  |
|                     |                                         |
|  Nuevo chat   (top) |          (center composition)           |
|                    |                                         |
|                    |                                         |
|                    |          Particle Sphere 240px           |
|                    |          ¿Qué desea consultar hoy?        |
|                    |          [ composer ]                    |
|                    |          approved-sources notice          |
|                    |                                         |
|  Ayuda y alcance    |                                         |
|  Cambiar tema       |                                         |
|  Perfil     (bottom)|                                         |
+--------------------------------------------------------------+
```

- **Sidebar rail:** fixed 64px wide, full height, border-right 1px `--warm-border` `#DDD9D1`. Compact icon rail. Top: `Nuevo chat`. Bottom group (stacked): `Ayuda y alcance`, `Cambiar tema`, `Perfil`. No history, no source list, no upload. Icons are 18–20px, 1.5px stroke; the rail uses icon-only controls with accessible labels and tooltips, NOT always-visible text labels. Each control exposes its label via `aria-label` and/or a `title` tooltip that appears on hover/focus; visible text labels are reserved for the header menu (mobile/tablet) where the rail collapses. Active/hover icon color in `--ink-blue` `#24445C`; default icon color in `--warm-gray` `#65615B`. Each item is a 44x44px minimum touch target.
- **Main area:** vertically centered initial composition (see §5). After first send, it becomes the conversation column (see §7) with the composer fixed at the bottom.

### 3.2 Tablet (768–1023px)

- Sidebar rail collapses to a header menu (see §3.3 mobile pattern, adapted to tablet width). Main area uses the standard 1024px-equivalent rhythm scaled down.
- Particle Sphere: **180px**.
- Composer and conversation column keep desktop structure with reduced horizontal padding (32px→24px).

### 3.3 Mobile (<768px)

- **No persistent sidebar.** A header bar contains: wordmark (left), a menu control (right) labeled `Menú` with a visible text label alongside the icon.
- The menu opens as an overlay from the top/right. Item order, top to bottom:
  1. `Nuevo chat` (first)
  2. `Ayuda y alcance`
  3. `Cambiar tema`
  4. `Perfil` (last)
- The menu respects the virtual keyboard: when the keyboard appears, the menu must not occlude the composer or its own last item. Use safe-area insets (`env(safe-area-inset-*)`) for top and bottom spacing. The composer docks above the keyboard with safe-area bottom padding.
- Particle Sphere: **140px**.
- Composer spans the viewport width minus 16px horizontal padding each side. Minimum 44px send hit target.
- The header bar uses `Position: sticky` semantics so it remains reachable but does not cover the conversation content.

---

## 4. Particle Sphere — visual signature

The Particle Sphere is a decorative visual signature only. It is NOT a logo, NOT an avatar, NOT a mascot, and NOT an interactive control. Treat it as `aria-hidden="true"` for assistive technology. Pointer interaction is decorative only and must never block normal touch scrolling.

Reference asset: `assets/ParticleSphere.tsx`. Behavior it implements (OpenDesign should match this intent, not necessarily the code):

- A performant Three.js `Points` cloud on a Fibonacci sphere (not 10,000 InstancedMesh geometries). Default point count lower on mobile/low-power (see `assets/ParticleSphere.tsx` defaults).
- **Colors (brand):** light theme `#24445C` (`--ink-blue`); dark theme `#7FA6BE` (`--ink-blue-bright`). Accept a `color` prop override.
- **Preview defaults:** `particleScale: 2`, `speed: 5`, `cursorRadiusUI: 50`.
- **Sizes:** 240px desktop, 180px tablet, 140px mobile. Parent controls size via a wrapping element; the component is responsive to parent dimensions, not to global state.
- **Pointer repulsion:** subtle, brand-colored. No hardcoded red displaced particles. Displaced particles stay within the brand hue family.
- **Click/tap scatter:** subtle outward scatter on pointer down, then re-settle. Touch-safe: must not prevent normal page scrolling.
- **Lifecycle:** stop/throttle the animation loop when `document.hidden`; clean up all listeners, animation frames, geometries, materials, and the renderer on unmount. Cap `devicePixelRatio` (see component).
- **Reduced motion:** render a static sphere (or very low-motion version), never remove it. The sphere is essential visual identity; reduced motion lowers motion, it does not blank the signature.
- **Lower-power fallback:** on low-power/mobile or if WebGL is unavailable, render a static, structural, non-gradient silhouette of the same hue and proportions (solid translucent disc or hairline ring). No radial gradients; the brand guide bans decorative gradients. When low-power is active, Three.js is never initialized (no WebGLRenderer, listeners, or animation frames); see `assets/ParticleSphere.tsx`, which gates the WebGL path behind an early return and renders the solid/structural fallback only.

**Lifecycle within the chat screen (choreography):**

1. **Initial state:** sphere centered, gently rotating, subtle pointer repulsion.
2. **On first send:** the sphere slightly reduces in scale, dims, and dissolves over **280–320ms** (brand motion range). Simultaneously the heading `¿Qué desea consultar hoy?` disappears. The sent user message rises into the conversation column. The composer settles to a fixed position at the bottom of the viewport.
3. **After dissolve completes:** the sphere is removed from the layout entirely (not just hidden behind content). It does not reappear for the remainder of the session.

Timing curve: ease-out with exponential feel (ease-out-quart/quint/expo). No bounce, no elastic. Animate opacity and transform only; never animate layout properties.

---

## 5. Initial (new session) center composition

Vertical center of the main area. Single staged idea. Stack order, top to bottom:

1. **Particle Sphere** (per §4).
2. **Heading:** `¿Qué desea consultar hoy?` — H1 (32px), Source Sans 3 600, `--charcoal` `#242321`, tracking slightly tight (-0.01em). Centered. One line on desktop; wraps gracefully on mobile.
3. **Composer** (see §8).
4. **Approved-sources / abstention notice** — caption (14px), `--warm-gray` `#65615B`, centered, max reading width 65–75ch. Exact copy:

   > Consultas con base en fuentes aprobadas. Cuando no existe evidencia, no se responde y se recomienda consultar a un especialista.

5. **Demo warning + non-corporate demo policy** — persistent, visible at all times, never dismissible on this prototype surface. Micro (12px), `--warm-gray` `#65615B`, centered, max reading width 65–75ch. Exact copy:

   > Entorno de demostración. No corporativo. Las consultas y respuestas son solo de muestra.

   This element must remain visible across all state variants (new session, generation, answer, abstention, provider unavailable, sensitive blocked, expiry). It is a non-negotiable safety affordance from `AGENTS.md`.

Spacing: 48px between sphere and heading, 32px between heading and composer, 24px between composer and the approved-sources notice, 16px between the approved-sources notice and the demo warning. On tablet/mobile reduce by one step (48→32, 32→24, 24→16, 16→12).

---

## 6. Ghost example queries (curated, rotating)

When a new session is active and the composer is empty and unfocused, rotate curated ghost example queries inside the composer placeholder. Rules:

- **Curated config only**, aligned to the approved corpus (runbooks, ADRs, policies). NEVER model-generated. OpenDesign must not invent its own examples; use the three below as the representative set.
- **Rotation:** every 4–5 seconds. **Fade only** (opacity, 220ms). No slide, no typewriter.
- **Stop on focus or typing.** When the composer gains focus or receives input, stop rotation and clear the placeholder per standard placeholder behavior.
- **Reduced motion:** show ONE static example (the first), do not rotate.

Three representative Spanish examples (formal, no unsupported specifics, no direct address):

1. `¿Cuál es el procedimiento para escalar una incidencia de infraestructura fuera del horario laboral?`
2. `¿Qué decisión de arquitectura se tomó para el almacenamiento de los índices de búsqueda?`
3. `¿Qué dice la política vigente sobre la retención de las consultas realizadas?`

---

## 7. Active chat — editorial conversation blocks

After the first send, the screen becomes a conversation column. **No conventional chat bubbles. No assistant avatar.**

Layout: a single centered column, max width 720px (narrow reading container), left-aligned text with comfortable horizontal padding. User and assistant entries are open editorial blocks separated by 32px vertical space.

### 7.1 User query block

- **Decisive alignment: left-aligned** within the single centered column, NOT right-aligned. Right-alignment is rejected because it breaks the editorial reading rhythm and risks a side-stripe reading. The user query is distinguished from the assistant answer by a subtle, contained treatment, not by alignment tricks:
  - A quiet container: `--ivory-light` `#FCFBF8` surface, 8px radius, 1px `--warm-border` border, 16px padding, max width ~85% of the column (so it reads as user voice, not full-bleed prose).
  - `--charcoal` `#242321`, Body (16px), Source Sans 3 400.
  - A small caption above the container (14px, `--warm-gray`): `Consulta`.
- The container is NOT a chat bubble (no tail, no side-stripe, no avatar). It is a restrained editorial block whose surface color subtly separates it from the assistant's answer block on the `--ivory` base.

### 7.2 Assistant answer block

- `--charcoal` `#242321`, Body L (18px), **Source Sans 3 400** for the answer body. Per `brand-guide.md`, Source Sans 3 is the default for UI and body, including dense repeated conversation answers. Source Serif 4 is reserved for a single major section opener/accent per surface and is NOT used in repeated chat answers. Reading width controlled to 65–75ch. Line height 1.5.
- **No assistant avatar, no assistant name, no "OpsKnowledge says" label.**
- Inline numbered citations render as superscript links: `¹`, `²`, `³`, in `--ink-blue` `#24445C`, focus ring 2px. Hover shows a subtle underline; no tooltip card (sources live in the disclosure below).
- Under each answer, a collapsed disclosure:

  **`Fuentes · 3`** (closed state; the number reflects actual citation count). Disclosure uses a native `<details>`/`<summary>` or equivalent semantic pattern with `aria-expanded` toggling. Chevron rotates 180deg over 220ms on open.

  **Expanded state:** each source item is a stacked block:

  - Document title (Body, 600, `--charcoal`)
  - Revision (Caption, `--warm-gray`): e.g. `Revisión 4`
  - Page (Caption, `--warm-gray`): e.g. `Página 12`
  - Exact excerpt (Body, **Source Sans 3 400**, `--charcoal`, max reading width), quoted.

  No side panel. Sources live inline under the answer, in the reading column.

### 7.3 Answer actions

Below the answer block (and below the sources disclosure), a quiet action row, left-aligned:

- `Copiar` — copies the answer text. On success, momentarily reads `Copiado`.
- `Útil` — affirmative feedback.
- `No útil` — negative feedback.

Negative feedback (`No útil`) may, without crowding the default state, reveal an inline follow-up offering the established support escalation and an optional comment field. Default state shows only the three action labels. The follow-up is a quiet inline expansion, NOT a modal.

All actions are text labels (no icon-only controls unless paired with a visible label). Each is a 44x44px minimum target.

---

## 8. Composer

The single input affordance. Lives centered under the heading initially; docks fixed at the bottom after the first send.

- **Multiline textarea** with capped growth: starts at ~1 line, grows to a maximum of ~5 lines, then scrolls internally. Growth does not animate layout; it snaps to content height.
- **Send:** button or `Enter` sends. `Shift+Enter` inserts a newline. The Send button label is `Enviar`.
- **During generation:** the Send button becomes `Detener` and aborts generation. Aborted generation does not persist a partial answer.
- **No controls attached to the composer:** no attachment button, no upload, no model selector, no language selector, no voice input.
- **Accessible label:** include a visually-hidden `<label>` (or `aria-label`) so the textarea is not labeled by placeholder alone. Placeholder text is presentational only.
- **Query-language detection is automatic** and invisible to the user. There is no visible language affordance.
- **Placeholder:** shows rotating ghost examples (§6) when applicable; otherwise shows a static placeholder: `Consulta técnica…`
- **Styling:** 8px radius, 1px `--warm-border` border, `--ivory-light` `#FCFBF8` surface (elevated above `--ivory` `#F7F5F0` base). Focus ring 2px `--ink-blue` `#24445C`. Text `--charcoal`, Body 16px.
- **Minimum 44px touch target** for the Send button.

---

## 9. State variants (OpenDesign must produce all)

Token colors reference the light palette unless marked. For dark, map `--ink-blue`→`#7FA6BE`, text/background per the dark palette table in `brand-guide.md`.

**Cross-variant invariant:** the demo warning and non-corporate demo policy (§5 item 5) MUST remain visible on every variant below, including errors and expiry. It is never hidden by a state transition.

### 9.1 New session (initial)
As §5. Sphere present, heading present, composer empty with rotating ghost examples, approved-sources notice present.

### 9.2 Generation in progress
- Sphere: mid-dissolve or already removed (depending on first-vs-subsequent send). For subsequent sends in an existing session, the sphere is already gone.
- The assistant block appears as a calm, explicit generation affordance: a quiet `--warm-gray` label `Generando respuesta…` with a restrained inline progress indicator (a single slow horizontal hairline or a single dot; NO letter-by-letter typing, NO animated shimmer over fake text, NO skeleton of fake answer content). A live region announces `Generando respuesta…` politely (`aria-live="polite"`).
- The composer Send button reads `Detener`.
- No answer text is shown until generation completes and is persisted.
- **Deterministic 10-second generation timeout:** generation has a bounded timeout of 10 seconds. If generation does not complete within 10 seconds, the UI transitions deterministically from the generating state to the provider-unavailable state (§9.6), using the exact provider-unavailable copy. Do NOT imply that generation retries. Do NOT show a partial or fabricated answer. No answer is persisted. The composer is re-enabled and a human expert is recommended. This timeout is a hard, visible UX deadline, not a silent retry loop.

### 9.3 Answer with collapsed sources
- Answer block (Source Sans 3) with inline numbered citations.
- Below it: `Fuentes · N` disclosure, closed.

### 9.4 Answer with expanded sources
- Same as 9.3 with the disclosure open; source items stack with title, revision, page, excerpt.

### 9.5 Abstention — missing / out-of-scope / contradictory evidence
Formal first-person voice, recommends a human expert, no fabricated specifics. Exact copy:

> No se pudo verificar esta información en las fuentes aprobadas. Se recomienda consultar a un especialista.

Do NOT echo the user question. Do NOT list sources (there are none). Show the quiet action row, but `Útil`/`No útil` are optional here; `Copiar` may copy the abstention text. The sources disclosure is absent (no `Fuentes · N`).

### 9.6 Provider unavailable
Distinct from missing evidence. State that the provider is unavailable, recommend a human expert, and confirm no answer was persisted. Exact copy:

> El proveedor de generación no está disponible. No se persistió ninguna respuesta. Se recomienda consultar a un especialista.

No citations, no sources disclosure, no answer text. The composer is re-enabled. This is a distinct message from §9.5.

### 9.7 Sensitive query blocked
A sensitive payload was detected and blocked before any model processing or persistence. NEVER echo the blocked text. Record only the blocking event (this is a UI-facing variant; the safe-field logging rule is a backend concern, not visual). Exact copy:

> La consulta fue bloqueada por contener información sensible. No se procesó ni se almacenó.

No citations, no sources disclosure. Composer re-enabled.

### 9.8 Session expiry / question-limit warning
Calm, non-blocking. Three sub-variants:

- **Five-minute inactivity warning (before expiry):** neutral, action-oriented copy with no direct address. Exact copy:

  > La sesión expirará en 5 minutos por inactividad. Para continuar, seleccionar `Extender sesión`.

  with an inline `Extender sesión` action (not a modal). Selecting it extends the session; the warning auto-dismisses. No question mark, no "¿Desea...?" direct-address phrasing.

- **Question-limit approaching (e.g., 20-question cap, warning near 18):** `Quedan N consultas disponibles en esta sesión.` (N = remaining). No block yet; informational only.
- **Limit reached:** `Se alcanzó el límite de consultas de la sesión. Se recomienda iniciar un nuevo chat.` with a `Nuevo chat` action that starts a fresh session.

- **Inactivity expired (actual expiry):** after the five-minute window elapses with no activity or extension, the usable conversation context is removed. The UI shows a clear, neutral message and readies the composer for a new session. Exact copy:

  > La sesión expiró por inactividad. El contexto de la conversación se eliminó. Para continuar, iniciar una nueva consulta.

  Behavior on expiry:
  - Conversation context (messages in the active session) is removed from the UI and from usable session memory; authorized analytical records are preserved (backend concern).
  - The composer is re-enabled and ready for a new session (it is NOT disabled).
  - Sensible focus moves to the composer so a keyboard user can immediately start a new query without hunting for focus.
  - The demo warning (§5 item 5) remains visible.
  - Do NOT show a modal. This is an inline state transition.

All warnings are inline, non-modal, dismissible (where applicable), and use caption/Body sizing in `--warm-gray` or `--charcoal` with appropriate contrast.

---

## 10. Accessibility (WCAG 2.2 AA)

- Keyboard operability: every action (send, stop, copy, feedback, sources disclosure, sidebar/menu items, theme toggle, profile) is reachable and operable by keyboard alone. Logical focus order. No keyboard traps.
- Visible focus: 2px focus ring (`--ink-blue` light / `--ink-blue-bright` dark) on every interactive element. Never remove focus outlines.
- Semantic disclosures: sources use `<details>`/`<summary>` or an equivalent with `aria-expanded`, `aria-controls`, and programmatic state. Feedback follow-up uses the same.
- Live regions: generation state uses `aria-live="polite"`; critical errors (provider unavailable, sensitive blocked) use `aria-live="assertive"` but remain calm visually.
- No placeholder as sole label: the composer has a hidden accessible label in addition to the visual placeholder.
- Reduced motion: all motion (sphere, ghost rotation, disclosure chevron, generation indicator) respects `prefers-reduced-motion: reduce`. Reduced motion shows a static sphere, one static ghost example, instant disclosure (no chevron rotation), and a static generation indicator.
- Hit targets: minimum 44x44 CSS px for every interactive element.
- Language: `<html lang="es">`. Per-block `lang` where mixed.
- Contrast: verify every text/background pair against 4.5:1 (normal) / 3:1 (large text, non-text) before release. Do not assume pairs are pre-audited.
- Color is never the sole indicator of state (e.g., feedback selected state uses both color and a visible mark/label).

---

## 11. Voice and copy rules (Spanish, formal, neutral)

Applied to every visible string. Mirrors `brand-guide.md` Voice.

- Formal, neutral, concise, discreet first person. Direct address ("usted"/"tu"/"ustedes") is avoided where a natural neutral construction exists, per `brand-guide.md` Voice. Screen-specific, explicitly approved formal prompts may use implied formal address sparingly; the sole approved exception on this screen is the initial heading `¿Qué desea consultar hoy?` (§5 item 2), recorded in `brand-guide.md`. No other direct-address copy is permitted on this screen without equivalent approval.
- Precise technical terminology. No humor, no emoji, no exclamation marks, no anthropomorphism, no artificial enthusiasm.
- No em dashes; use commas, colons, semicolons, periods, parentheses.
- Abstention copy uses the §9.5 template. Provider-unavailable copy (§9.6) is distinct and states no answer was persisted. Sensitive-block copy (§9.7) never echoes blocked text.
- Every technical claim in an answer references an inline numbered citation to a current approved source.

---

## 12. Explicit "do not invent" list

OpenDesign must NOT introduce any of the following, even if common in chat UIs:

- Document upload, attachment, or file ingestion UI.
- Persistent chat history across sessions or a sidebar history list.
- A source library, source management, or reranking control.
- A model selector or language selector.
- An admin dashboard or top-level admin surface (admin is conditional inside Profile only).
- Gradients of any kind, gradient text, glassmorphism, blur decoration, decorative illustrations, mascots, avatars, stock photography, floating cards, side-stripe accents.
- Generic purple/blue "AI" styling, neon, animated blobs, dark-by-default theming.
- Letter-by-letter typing animation for generation.
- Tooltips for citations (sources live in the disclosure).
- Modals as the first interaction pattern for feedback, warnings, or sources.

---

## 13. Deliverable checklist for OpenDesign

- [ ] Desktop, tablet, and mobile layouts per §3.
- [ ] Initial center composition per §5 with exact Spanish copy, including the persistent demo warning and non-corporate demo policy.
- [ ] Particle Sphere matching `assets/ParticleSphere.tsx` intent, brand colors, three sizes, reduced-motion and non-gradient lower-power fallbacks.
- [ ] First-send choreography (280–320ms dissolve, heading removal, message rise, composer dock) per §4.
- [ ] Composer per §8 with accessible label, Enter/Shift+Enter, `Enviar`/`Detener`, no extra controls.
- [ ] Ghost example rotation per §6 with the three curated examples, fade only, reduced-motion static.
- [ ] Active chat editorial blocks per §7 (no bubbles, no assistant avatar, left-aligned user query in a subtle container, inline citations, `Fuentes · N` disclosure with title/revision/page/excerpt).
- [ ] Answer actions `Copiar`, `Útil`, `No útil` with quiet negative-feedback follow-up (no modal).
- [ ] All state variants per §9 with exact Spanish copy, including deterministic 10-second generation timeout and inactivity-expired state.
- [ ] Demo warning and non-corporate demo policy visible on every variant.
- [ ] Accessibility per §10.
- [ ] Voice and copy rules per §11; no em dashes, direct address avoided except the approved heading exception, no humor.
- [ ] Nothing from the §12 "do not invent" list appears.
- [ ] No decorative gradients of any kind (including in the ParticleSphere fallback).

---

## 14. Future validation checklist (runtime integration)

This repository currently has no runtime/test stack, so the checks below are NOT executed now. They are the acceptance gate for when the bootstrap stack lands (per `AGENTS.md`). Do not claim any of these pass today.

**ParticleSphere runtime validation (to run with a real React + Three.js stack):**

- [ ] WebGL unavailable: component renders the non-gradient fallback deterministically, no exception, no blank canvas.
- [ ] WebGLRenderer constructor failure (e.g. forced context loss at construction): component catches and renders the fallback, no unhandled rejection.
- [ ] `webglcontextlost` event fires at runtime: component removes the canvas, activates the fallback, and cleans up listeners (no orphaned rAF or listeners).
- [ ] Zero-size initial mount: a parent that starts at 0x0 and later reports usable dimensions via ResizeObserver causes the renderer to initialize on the first usable report (driven by a distinct `readySignal` state, not `useFallback`), no permanent blank sphere. Observer cleans up and no state update fires after unmount.
- [ ] Prop boundaries: `count` of 0, 1, negative, non-finite, or oversized finite (e.g. 100000) does not throw; `count=1` renders a single valid point; oversized finite values clamp to `MAX_PARTICLES` (20000) without allocation spike; `speed` of 0 produces no rotation; `particleScale` of 0 renders zero-size points without error.
- [ ] `prefers-reduced-motion` media query changes at runtime (toggled while mounted): the component updates its motion behavior without requiring an unrelated prop render.
- [ ] Hidden tab (`visibilitychange`): the animation loop pauses work while `document.hidden` and resumes when visible, with no frame storm on return.
- [ ] Resize: changing the parent dimensions updates the renderer and camera aspect without duplication or blank frames.
- [ ] Cleanup on unmount: after unmount, no leaked rAF, listeners, geometries, materials, or renderer remain (verify via a leak probe).
- [ ] Touch scrolling: a page with the sphere scrolls normally on touch devices; pointer interaction never calls `preventDefault` and never traps gestures.
- [ ] Reduced motion: static sphere renders once, no rAF loop, no accumulation.

**Main screen UX validation (to run with a real frontend stack):**

- [ ] Deterministic 10-second generation timeout transitions to provider-unavailable copy within the bounded window, no partial answer, no retry implication.
- [ ] Inactivity expired: conversation context removed, composer re-enabled, focus moves to composer, demo warning persists.
- [ ] Demo warning present on every variant per §9.
- [ ] Keyboard walkthrough: every action reachable and operable; no traps; visible focus on all controls.
- [ ] Contrast: every text/background pair passes WCAG 2.2 AA.