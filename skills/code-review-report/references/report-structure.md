# Report structure

## Sections

Keep this order: **overview, design decisions, changes in detail, verification, impact, unfinished, review checklist**. For small changes, merge sections to avoid inflation. Drop sections that don't apply, or leave "N/A + reason" in one line.

1. **Header** — title (task name), one-line summary, meta (scope, date, links to related docs/issues). No hype. Related links live here.
2. **Table of contents** *(conditional)* — anchor links. Only when there are many sections; skip for short reports.
3. **Overview** — what was done and why, the problem and requirements it addresses, big picture first. Name the top one or two P1 findings here in a single line each, so the reviewer catches the main suspicions without scrolling to the checklist at the bottom. For small changes, absorb the key design decisions here.
4. **Key design decisions** — per decision: what was decided / why / rejected alternatives and tradeoffs. Saves the reviewer from wondering "why was it done this way?".
5. **Changes in detail** — by file or by theme. Each change gets a code quote (before→after when possible) and its intent. Not a flat list — state what each change is for.
6. **Verification** — make the change reproducible for the reviewer: tests added, manual scenarios, copy-pasteable commands. Result summaries ("144 tests pass") are facts — fine to state in prose. This is narrative, not the badge images CI generates. If nothing was verified, say so.
7. **Impact / compatibility** — other modules touched, external API contracts, migrations, backward compatibility. One line if small. For UI changes, embed before/after screenshots (single-file HTML can embed images). "N/A" if none.
8. **Unfinished / next steps** — make incomplete work visible (todo badge).
9. **Review checklist** — what the reviewer should doubt and verify, prioritized P1–P3. Each item: why it's suspicious + where to look (file:line). Risks belong here as priorities, not in a separate section.

## Leave out (PR-only elements)

This report is reference material that supports review, not a merge/deploy gate. Don't blur that:

- Merge checkboxes, "Definition of Done" lists — they read as todo lists.
- CI/test/coverage badge images — those are CI artifacts, not something to hand-place in static HTML. Stating "N tests pass" as prose in the Verification section is fine (a factual statement, not a badge).
- A standalone risk/rollback section — that's for deploy decisions. Risks go into the review checklist as P1s.
- Changelog-style exhaustive listing — flat lists without intent or why. This document is not a changelog.
- Release-notes marketing tone — the audience is a reviewer, not an end user.
- ADR status (Proposed/Accepted) and approver metadata — governance overhead, too much here.

## Review navigation (footnotes linking code ↔ findings)

In a long report the reviewer must be able to jump from a change in "Changes in detail" to its finding, and from a checklist item back to the code. Don't make them scroll — connect both directions with anchors.

- Give each review-checklist item an `id` (`<div class="check" id="r1">`).
- In change details, attach a **superscript footnote link** where the finding applies: `...this one line<sup><a href="#r1">P1</a></sup>.`
- Each checklist item gets a **back-link** (`↩`) to the related change detail (give that heading an `id` too).
- Include the review checklist in the table of contents; if there are many items, at least make the P1s jumpable.

## Self-check

After writing the report, re-read it once:

- Color overused anywhere (style-guide violation)?
- Any change description missing its "why"?
- Unfinished work stated honestly, or dressed up as "all done"?
- Does the checklist point at real suspicions, or just platitudes?
- Are footnote anchors paired both ways (`href="#rN"` in change details ↔ `id="rN"` in the checklist, no dead links)?
