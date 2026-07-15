# OpsKnowledge UI Brand Specification

Derived from `brand-guide.md`, the authoritative source for this prototype.

## Tokens

```css
:root {
  --bg: oklch(97.03% 0.0070 88.64);
  --surface: oklch(98.80% 0.0041 91.45);
  --fg: oklch(25.65% 0.0040 84.58);
  --muted: oklch(49.44% 0.0107 78.23);
  --border: oklch(88.62% 0.0117 84.58);
  --accent: oklch(37.34% 0.0561 242.68);

  --font-display: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
  --font-body: "Source Sans 3", "Segoe UI", system-ui, sans-serif;
  --font-editorial: "Source Serif 4", Georgia, serif;
  --font-mono: "IBM Plex Mono", "Cascadia Mono", ui-monospace, monospace;
}
```

## Layout Posture

- Use type and whitespace before containers, fills, or decoration.
- Use 8px radii for controls and 12px only for substantial panels.
- Use 1px warm hairlines; shadows are exceptional and low elevation.
- Reserve ink blue for primary actions, links, focus, and key data.
- Limit Source Serif 4 to one major opening line per surface.

## Motion Posture

- Keep transitions between 220ms and 320ms with exponential ease-out.
- Animate opacity and transforms only.
- Return immediate interaction feedback within 100ms.
- Remove nonessential motion under `prefers-reduced-motion: reduce`.
