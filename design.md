# Design: Athem Ventures and PerformanceReach

The locked system. Every Hallmark run reads this first and pages share it. Change it on purpose; the file is the rule.

## System
- Genre: modern-minimal
- Shape of the first page: Control Room (architecture), Split field (sign-in), app screen (Growth Studio and the harness registry)
- Theme: custom (vibe: "Flat primary colour, printed, exact")
- Axes: light/geometric-sans/chromatic-blue · posture: Full palette (Committed on the sign-in screens)
- Idea: status is light. Red is stopped, blue is being built, green is live. Every page keeps score in those three, and a word always rides with the colour.

## Tokens
`assets/tokens.css` is the source of truth. The roles:
```css
:root {
  --color-paper: oklch(98.4% 0.005 255);  --color-paper-2: oklch(95.6% 0.007 255);  --color-paper-3: oklch(91.5% 0.01 255);
  --color-ink: oklch(17% 0.025 265);  --color-ink-2: oklch(32% 0.025 265);  --color-muted: oklch(46% 0.025 265);  --color-rule: oklch(86% 0.01 258);
  --color-blue: oklch(47% 0.285 264);  --color-green: oklch(66% 0.215 148);  --color-red: oklch(55% 0.24 28);
  --color-accent: var(--color-blue);  --color-accent-ink: oklch(98.4% 0.005 255);  --color-focus: oklch(47% 0.285 264);
  --font-display: "Funnel Display", ui-sans-serif, system-ui, sans-serif;
  --font-body: "Funnel Sans", ui-sans-serif, system-ui, sans-serif;
  --font-outlier: "JetBrains Mono", ui-monospace, monospace;  /* identifiers and code only */
  --radius-card: 0;  --radius-control: 2px;  --rule-hair: 1px;  --rule-heavy: 4px;  --shadow-card: none;
}
```
Each primary also has a `-ink` (text on it), a `-wash` (tinted surface) and a `-text` (text on paper) token. Green fills carry dark ink, never white. The spacing scale, the type scale, the easings and the durations are the scaffold's and live in `tokens.css`.

## Status
- Not started, failed, stopped: red, square glyph.
- Scaffolded, being built, the current place, the primary action: blue, triangle glyph.
- Operational, approved, connected, live: green, circle glyph.
- A status is a filled block with its word inside. Colour never works alone.

## Controls
- Primary: blue fill, paper text, 2px radius, 40px high in app screens and 48px on sign-in screens. One per page.
- Secondary: 1px ink outline, same height and radius.

## Motion
- Character: still. State changes are colour and a 1px press. One panel slide on the architecture page. Under reduced motion everything ends at once.

## Exports
`assets/tokens.css` in this project. Tailwind, DTCG or shadcn blocks are added here on request, per `export-formats.md`.
