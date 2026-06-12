# Style guide — minimal report

**Hierarchy comes from typography, spacing, and contrast — not color.** The look of a quiet, typography-first engineering blog.

The CSS in `assets/template.html` is the single source of truth for styling. Don't restyle it. This file states the rules that CSS encodes, so you can extend the report without breaking them.

## Palette (don't leave these values)

Mirrors the template's `:root` variables — the template is authoritative.

| Use | Value | Note |
|-----|-------|------|
| Background | `#faf9f6` | Warm off-white. Pure white (#fff) also allowed |
| Body text | `#1a1a1a` | Near-black |
| Secondary text | `#6b6b6b` | Captions, meta, descriptions |
| Borders / rules | `#e5e3dd` | Very light |
| Code background | `#f4f2ec` | Slightly darker off-white than the page |
| Accent | `#b8512e` **one and only** | Links, heading emphasis, important marks. Muted terracotta. Don't overuse |

**Never:**

- Vivid/neon colors, gradients
- Multi-color background blocks (mixing blue, green, yellow boxes)
- Heavy box shadows (`box-shadow` almost never; if at all, very light)
- Distinguishing priorities (P1/P2/P3) or badges by color alone — use text labels and light borders

One accent color, total. Don't grow the palette ("red for important, yellow for warning"). When something needs emphasis, use **weight or a small label**, not a new color.

The single exception is syntax highlighting inside code blocks. Token colors exist for code readability, so they're exempt from the one-color rule — but they stay muted there too (see below).

## Typography & layout

- System sans-serif stack; body `17px` / line-height `1.7`.
- Hierarchy by **size and weight**: h1 30–34px, h2 22–24px (large top margin to separate sections), h3 18–19px — all weight 600.
- Centered narrow column (`max-width: 740px`), generous spacing between sections. Don't pack the page.
- Table of contents as an inline anchor list at the top. Keep it simple.

## Code blocks

- A colorless wall of code is hard to read — **syntax highlighting is required**. Highlight.js is vendored in `assets/` and inlined by `scripts/inline_hljs.py`; no CDN, the report works offline.
- Always set a language class so highlighting applies: `<pre><code class="language-python">`.
- Token colors are "quiet highlighting": only keywords, strings, comments, and numbers get muted colors; everything else inherits body text. The exact colors live in the template — don't brighten them.
- Inline code: same background, no highlighting.
- For before→after, stack two blocks with small labels ("Before" / "After"). Labels, not red/green diff colors — save the color budget.

## Tables

- Header row: weight 600, `2px` bottom border.
- Body rows: `1px` bottom border only — no vertical lines, no zebra stripes.
- Left-aligned.

## Badges & emphasis (unfinished work / priorities)

Express with **a label plus a light border**, not color fills (`.badge` in the template).

- The accent-colored "⚠️ TODO" badge appears about once. More and the color restraint collapses.
- P1/P2/P3 are plain text labels. Don't paint them.

## Tone

- No marketing language, no hype. Calm and factual.
- Almost no emoji (the ⚠️ on the unfinished-work badge is the exception).
- Dense in information, quiet in appearance — "quiet but packed" is the target.
