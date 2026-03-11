---
name: github-review-pr
version: 0.1.0
category: productivity
description: "Analyze a GitHub pull request and produce a review report covering changes, review status, and code quality."
argument-hint: "<pr-number or URL>"
---

# GitHub PR Reviewer

Analyze a GitHub pull request and produce a structured review report.

## Use this skill when

- Reviewing a PR before approving or requesting changes
- Getting a quick overview of a large PR
- Summarizing review status and unresolved comments

## Do not use this skill when

- The user wants to write a PR description (use write-pr)
- The user wants to merge, edit, or comment on a PR
- The user wants to check for duplicate issues (use github-review-check-duplicate)

## Instructions

### Step 1: Parse Input

`$ARGUMENTS` is a PR number or GitHub URL.

- URL (e.g., `https://github.com/owner/repo/pull/123`): extract `owner/repo` and PR number, use `-R owner/repo`
- Number only: use the current repository
- If ambiguous, ask the user for the exact PR number or URL

### Step 2: Fetch Data

```bash
gh pr view <number> [-R owner/repo] --json title,body,state,commits,files,additions,deletions,author,baseRefName,headRefName,createdAt,mergedAt,isDraft,mergeable,comments,reviews,reviewDecision,reviewRequests
gh pr diff <number> [-R owner/repo]
```

If the `reviews` array is not empty, fetch review comments:

```bash
gh api repos/{owner}/{repo}/pulls/{number}/comments
```

### Step 3: Analyze

#### PR Summary
- Title, state (open/merged/closed), author
- Branch: `head` → `base`
- Draft status, mergeable state
- Created date and merge date (if merged)

#### Changes Overview
- Files changed, lines added/deleted
- Key change areas by directory (source, tests, config, docs)
- High-risk changes (core logic, migrations, auth/security)

#### Commit Analysis
- Commit list with intent of each commit

#### Review Status
- Review decision (APPROVED, CHANGES_REQUESTED, REVIEW_REQUIRED, etc.)
- Requested reviewers
- Per-reviewer feedback:
  - Review state (approved / changes requested / commented)
  - Key feedback summary
- Unresolved review comments with core content
- Agreed vs. unresolved items

#### Code Review
- Code quality observations
- Potential issues (bugs, performance, security, regressions)
- Improvement suggestions (prioritized)
- Test coverage assessment (gaps, additional tests needed)

### Step 4: Large PR Handling

If the file count is 30+ or additions exceed 1000:
- Focus diff analysis on source code files
- Provide summary-only for tests, config, and generated files (lock files, snapshots, etc.)
- State the analysis scope in the Changes Overview

### Step 5: Output Rules

- State facts. Mark uncertain observations as estimates.
- Classify issues by severity (High / Medium / Low).
- Reference file paths as evidence where possible.

## Constraints

- Use `gh` CLI for all GitHub PR queries.
- Do not modify PR state (edit, merge, comment) unless explicitly requested.
