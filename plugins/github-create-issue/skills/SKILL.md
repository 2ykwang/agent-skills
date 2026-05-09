---
name: github-create-issue
version: 0.1.0
category: productivity
description: "File a GitHub issue maintainers can actually act on — verified, not a duplicate, follows repo conventions (template/label/prefix), and previewed before publishing. Use when reporting a known problem."
---

# github-create-issue

## Core principles

1. **Objectivity is the signal.** Avoid phrases like "looks good." Show impact scope and estimated difficulty in concrete terms.
2. **Never upload without user confirmation.** Show the exact final form (title, body, labels, repo) and get explicit approval before publishing.

## Workflow

There are decision points between steps where user input is needed — don't try to do everything at once.

Throughout: use repo context (`git log`, branch names, existing issues, labels) to infer conventions before defaulting or asking the user. The repo usually answers most "how should this look?" questions — language, prefix style, body structure, label vocabulary.

### 1. Confirm intent (ask back if unclear)

Check that all four are clear enough:

- **What is the problem/request?** (Can it be summarized in one sentence?)
- **Where was it found?** (Specific code/UX/doc — can the verification target be identified?)
- **What outcome does the user want?** (A fix? A discussion RFC? Documentation?)
- **Body language** (the issue body language may differ from the conversation language — match the repo's existing convention; ask once if unclear.)

If any is ambiguous, don't proceed — ask back briefly. Examples:

| Ambiguous item | Example follow-up |
|---|---|
| What | "What behavior is the problem? In one line." |
| Where | "Which screen/module is affected?" |
| Outcome | "Is this a fix request or an RFC for collecting opinions?" |
| Language | "Body language — Korean or English?" |

If multiple are ambiguous, **ask the single most decisive one first**. Throwing 3-4 questions at the user at once just adds load and dilutes the answers. One wrong direction in exploration makes both verification and writing useless.

### 2. Verify (real issue + no duplicates)

**Check duplicates first.** If a similar issue already exists, don't create a new one — comment on it or reference it instead:

```bash
gh issue list --search "<key keywords>" --state all --limit 10
```

Use the most identifying 1-2 nouns from the user's claim (`.DS_Store`, `dark mode`, `cache key`, etc.). If similar issues appear, ask the user — "Create a new one or add to existing #X?" — before proceeding.

**Then verify the facts.** By issue type:

- **Bug**: grep related code; if possible, reproduce via `ls`/`find`/run in the actual environment
- **Improvement/feature**: confirm the current behavior actually does what the user claims (code/run output)
- **Docs/UX**: confirm the file/screen actually does that

If only partially correct, or if the cause is different, **don't post as-is — tell the user**. A wrong issue is permanent noise.

If verification is hard or environment-dependent, say so explicitly — don't fill in by guessing.

### 3. Estimate value and difficulty

Estimate in concrete numbers so the user can judge priority.

Value signals:
- Percentage of users affected (measure if possible, otherwise state estimation basis)
- Quantitative impact: disk/performance/security
- Frequency and intensity of UX noise

Difficulty signals:
- Estimated lines of change (N lines code, M lines tests)
- Number of files and invariants affected
- Boundaries that may break (cross-file sync needed?)

If the numbers are small, report small. "Low", "30 min – 1 hour" — be honest. No exaggeration.

### 4. Decide classification

| Situation | prefix |
|---|---|
| Broken behavior / unexpected result | `bug:` |
| Existing behavior is intentional but a better direction exists | `improve:` or `enhancement:` |
| New feature | `feat:` |
| Discussion / docs / meta | `docs:`, `chore:`, `discuss:` |

**Detect the project's convention first** — scan `git log --oneline -20` and recent issue titles (`gh issue list --limit 10 --state all --json title -q '.[].title'`). If most samples follow a single prefix style (e.g., `feat:`/`fix:` for conventional-commits, `[BUG]`/`[#NUM]` for bracket style, plain sentence-case for no-prefix), follow it. If mixed or unclear, omit the prefix — a wrong prefix is worse than no prefix. The table above shows conventional-commits as one default; apply only when the repo confirms that style.

If the user specified a prefix directly, use that unconditionally. **Don't classify as `bug:` arbitrarily** — the same phenomenon can be a "bug report" or a "behavior redefinition request" depending on user intent.

### 5. Choose template

Priority:

1. **Current repo's `.github/ISSUE_TEMPLATE/`**
   - `ls .github/ISSUE_TEMPLATE/` or `find .github -path '*ISSUE_TEMPLATE*'`
   - YAML form (`*.yml`): convert fields to markdown headers (`### Field name`)
   - Markdown (`*.md`): follow as-is
2. **No template in repo → reference existing issues**
   - `gh issue list --limit 5 --state all --json title,body | jq -r '.[].body'`
   - Follow recurring section headers if present
3. **Neither → fall back to `references/issue_templates.md`**
   - Use the skeleton matching the classification (bug/feat/improve/discuss/docs)

Report which template was used and where it came from in one line.

**Label consistency check.** Verify the label expected from classification (Step 4) actually exists in the repo:

```bash
gh label list --json name -q '.[].name'
```

By situation:
- Label exists → use it
- Similar label exists (e.g., no `discuss`, only `enhancement`) → ask user "Use similar X, or no label?"
- No suitable label → proceed without label, or get consent to create new (`gh label create`)

Publishing with classification and label mismatched leads to wrong triage.

### 6. Choose length

Recommend a default and ask the user — short for small problems, medium+ if design decisions are involved.

| Length | Volume | When |
|---|---|---|
| **short** | 2-5 line body | Self-evident small improvements, clear bugs |
| **medium** | 8-15 line body + 1-2 sections | Typical issues. Separate problem / rationale / expected behavior |
| **long** | 20+ line body + multiple sections | Design changes, option comparisons, external context needed |

Length is a tool for **signal clarity**, not information density. If short suffices but you use long, the signal gets buried.

### 7. Write body (2 versions)

Make **2 versions of title and body** with the chosen template and length. The two versions must differ meaningfully — copies with a few words swapped are useless.

Differentiation axis examples:
- **A**: problem-focused (what's wrong with current behavior)
- **B**: solution-focused (what the desired behavior is)
- If classification splits: **A = bug:**, **B = improve:**

Add a one-line "why this version" to each so they're comparable.

Writing principles:
- **Skip self-evident mechanics.** What's already obvious from reading the code doesn't need to be in the body.
- **Reproduction coordinates only when non-obvious.** Skip when obvious; include when surprisingly located.
- **Focus on the "why is it needed" context.** Intent before phenomenon.
- Body language was already decided in Step 1 — don't re-ask, follow that decision.

### 8. Upload preview + consent

Show the exact form to be published:

```
[A or B - user choice]

repo: <owner>/<name>
title: <final title>
labels: <label list>
body:
---
<final body>
---

Upload as-is?
```

Confirm repo via `git remote get-url origin` or `gh repo view --json nameWithOwner -q .nameWithOwner`. If auto-detection is ambiguous, ask the user.

Use labels auto-attached by template as-is (e.g., `bug_report.yml` → `bug` label). If additional labels are needed, ask consent.

**Don't upload without OK.** If revision is requested, polish only the chosen version and re-preview.

### 9. Publish + report URL

```bash
gh issue create --title "..." --label "..." --body "$(cat <<'EOF'
...
EOF
)"
```

Body must use heredoc (avoids backtick / quote escaping).

On success, report the URL in one line. On failure (auth / permission / missing label), show the raw error and decide the next step with the user.
