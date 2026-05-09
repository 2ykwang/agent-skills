# Fallback Issue Templates

Use only when the repo has no `.github/ISSUE_TEMPLATE/` and no existing issues to reference. Adjust length (short/medium/long) by body volume.

Don't try to fill empty sections — drop them.

`< ... >` are placeholders. Replace with actual content when writing.

---

## bug — broken behavior

prefix `bug:`, label `bug`

```
### What happened

<observed phenomenon>

### Expected

<expected behavior>
```

If reproduction is non-obvious, add `### Steps to reproduce` and fill `<reproduction steps>`.

---

## feat / improve — improvement / new feature

prefix `feat:` or `improve:`, label `enhancement`

```
### Problem

<why current behavior is insufficient, or what scenario is blocked>

### Proposal

<desired change — what shape it should take>
```

Add `### Alternatives` only when alternative comparison is meaningful, and fill `<other approaches considered and why not chosen>`.

---

## discuss — decision / discussion (RFC)

prefix `discuss:` or `rfc:`, label `discussion` (omit label if absent)

```
### Context

<why is this discussion needed now, what triggered it>

### Question

<core question to decide>

### Options

- <option A description, pros/cons>
- <option B description, pros/cons>
```

If only one option, drop `### Options` and merge into a single `### Proposal` section.

---

## docs — documentation

prefix `docs:`, label `documentation`

```
### Where

<doc location — file, section, URL>

### Issue

<what is missing, wrong, or confusing>
```

Most end in two lines.

---

## Notes on use

- Header level (`###` vs `##`) and prefix conventions follow the repo's tone.
- If a section not in the skeleton is genuinely needed (e.g., `### Impact` for security), add it.
- Conversely, drop skeleton sections that are noise. If a "self-evidently reproducible bug" feels awkward ending in a one-line `### Expected`, merge two sections into one paragraph.
