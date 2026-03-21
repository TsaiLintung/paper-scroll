# Visual Style Guide

A clean, editorial aesthetic — quiet greens, warm darks, and a mix of serif and sans-serif that feels like a well-designed academic journal.

---

## Typography

Three typefaces, each with a distinct role:

| Role | Font | Fallbacks |
|---|---|---|
| Display / wordmark | Cormorant Garamond | Playfair Display, Georgia, serif |
| Body / UI | Source Sans 3 | Myriad Pro, system-ui, sans-serif |
| Content titles | Source Serif 4 | Minion Pro, Georgia, serif |

**Usage rules:**
- **Wordmark / page title:** Cormorant Garamond 500, `letter-spacing: 0.4em`, uppercase feel — sparse and elegant.
- **Section labels:** Source Sans 3, `0.68rem`, `font-weight: 600`, `text-transform: uppercase`, `letter-spacing: 0.14em`, muted color — acts as a quiet structural marker.
- **Article/card titles:** Source Serif 4, `1.1rem`, `font-weight: 500`, `line-height: 1.4`.
- **Body text:** Source Sans 3, `16px` base, `line-height: 1.6`; abstracts/long-form use `line-height: 1.65`.
- Font smoothing: always `antialiased`. `text-rendering: optimizeLegibility`.

---

## Color Palette

All colors live as CSS custom properties on `:root` with a `[data-theme="dark"]` override.

### Light mode
```css
--color-bg:            #ffffff
--color-surface:       #ffffff
--color-text:          #0f1a15   /* near-black with a green undertone */
--color-text-muted:    #4e7a66   /* mid green, used for meta, labels */
--color-accent:        #3eb489   /* primary green */
--color-accent-hover:  #2d8a6c
--color-border:        #c8e6d5
--color-border-subtle: #e9f5ef   /* hairline dividers */
--color-border-input:  #c2ddd2
--color-error:         #c62828
--color-error-border:  #f5c2c0
--color-overlay:       rgba(255, 255, 255, 0.94)
--color-title-ink:     #1c1208   /* warm near-black for display type */
```

### Dark mode
```css
--color-bg:            #111c17
--color-surface:       #182419
--color-text:          #e0f0e8
--color-text-muted:    #7ab898
--color-accent:        #3eb489   /* same accent, works on both */
--color-accent-hover:  #5ecfa5
--color-border:        #253d2e
--color-border-subtle: #1e3028
--color-border-input:  #2e5040
--color-error:         #f28b82
--color-error-border:  #5c2020
--color-overlay:       rgba(17, 28, 23, 0.94)
--color-title-ink:     #e8d9c0   /* warm cream for display type */
```

> The green family is the identity of the palette — greens run through text, borders, and the accent. It reads as natural and calm, not tech-brand.

---

## Layout

- **Max content width:** `720px`, centered with `margin: 0 auto`.
- **Padding:** `20–24px` horizontal on cards and panels; `28px` on settings-style panels.
- Full-height shell via `height: 100vh` with flex/grid column layout.
- Panels (e.g. side drawers) slide in from the right, `max-width: 480px`, separated by a single `1px` border.

---

## Components

### Buttons

**Ghost / outline (primary action):**
```css
padding: 6px 16px;
border-radius: 999px;
border: 1px solid var(--color-accent);
background: transparent;
color: var(--color-accent);
```
On hover: fill with `--color-accent`, text becomes surface color.

**Ghost / muted (secondary / destructive):**
```css
border: 1px solid var(--color-border-input);
color: var(--color-text-muted);
```
On hover: border and text shift to `--color-error`.

**Icon buttons:** circular (`border-radius: 50%`), transparent background, `36–52px`. Icons inverted in dark mode via `filter: invert(1)`.

### Inputs

Underline-only style — no box border:
```css
border: none;
border-bottom: 1px solid var(--color-border-input);
background: transparent;
padding: 6px 0;
```
On focus: `outline: none`, bottom border color → `--color-accent`.

### Chips / Tags

```css
border: 1px solid var(--color-border-input);
border-radius: 999px;
padding: 4px 10px 4px 12px;
font-size: 0.8rem;
background: transparent;
```
Remove button inside chip changes color to `--color-error` on hover.

### Dividers

Single-pixel `background: var(--color-border-subtle)` — barely there.

---

## Motion

Short, subtle transitions only:
- **Interactive elements** (buttons, inputs, color changes): `150ms ease`
- **Toggles**: `200ms ease`
- **Structural reveals** (header collapse, overlay): `250–350ms ease`

No bouncing, no springs — everything fades or slides calmly.

---

## Tone Summary

- **Quiet and editorial** — the UI recedes; content leads.
- **Green as identity** — not decorative, but structural (borders, muted text, accents all share the same hue family).
- **Generous whitespace** — padding errs on the larger side; elements breathe.
- **Minimal chrome** — ghost buttons, underline-only links, hairline borders. Nothing filled or heavy unless actively hovered.
- **Serif for content, sans for UI** — a classic editorial split that signals "reading environment."
