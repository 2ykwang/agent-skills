---
name: github-review-check-duplicate
version: 0.1.0
category: productivity
description: "Check if a GitHub issue is a duplicate and find related issues and PRs."
argument-hint: "<issue-number or GitHub URL>"
---

# GitHub Duplicate Issue Checker

Analyze an issue to determine if it is a duplicate and find related issues and PRs.

## Use this skill when

- A new issue is filed and needs duplicate checking before triage
- Searching for existing issues or PRs related to a specific issue
- Deciding whether to close an issue as a duplicate

## Do not use this skill when

- The user wants a general issue summary (use github-review-issue)
- The user wants a PR review (use github-review-pr)
- The user wants to create or edit issues

## Instructions

### Input

`$ARGUMENTS` is an issue number or GitHub URL.

- URL (e.g., `https://github.com/owner/repo/issues/749`): extract `owner/repo`, use `--repo` flag
- Number only: detect current repo via `gh repo view --json nameWithOwner -q .nameWithOwner`

### Step 1: Fetch Issue Details

```bash
gh issue view $ARGUMENTS --json number,title,body,labels,author,createdAt,comments
```

- Extract key terms from title and body
- Check comments for ongoing discussion and referenced issues/PRs
- Classify issue type (bug report / feature request / question / other)
- Note error messages, stack traces, and specific file names

### Step 2: Multi-Angle Search

A single search is insufficient. Use multiple strategies:

#### 2-1. Keyword Search (at least 2-3 variations)

```bash
gh search issues "<original keywords>" --repo {owner/repo} --limit 20
gh search issues "<synonym keywords>" --repo {owner/repo} --limit 20
gh search issues "<error code or filename>" --repo {owner/repo} --limit 15
```

Examples:
- Original: "login fails" → Synonym: "authentication error", "sign in broken"
- Original: "500 error" → Related: "internal server error", "server crash"

#### 2-2. PR Search

```bash
gh search prs "<keywords>" --repo {owner/repo} --limit 15
```

#### 2-3. Label-Based Search (if labels exist)

```bash
gh issue list --label "<related label>" --state all --limit 20 --json number,title,state --repo {owner/repo}
```

#### 2-4. Cross-Reference Check

```bash
gh api repos/{owner}/{repo}/issues/{issue-number}/timeline --jq '.[] | select(.event == "cross-referenced")'
```

### Step 3: Analyze Candidates

For the top 5-10 similar issues from search results, fetch details:

```bash
gh issue view <number> --repo {owner/repo} --json number,title,body,state,comments
```

- Determine if similarity is superficial (title only) or substantive (same problem)
- Check if they share the same root cause
- Check if already resolved (closed + resolution comment)
- Look for related PRs mentioned in comments

### Step 4: Duplicate Criteria

Mark as **duplicate** if any of the following apply:

| Criterion | Example |
|-----------|---------|
| Same bug/error | Same error message, same reproduction steps |
| Same feature request | Different wording but identical desired functionality |
| Same question | Asked differently but seeking the same answer |
| Same root cause | Different symptoms but same underlying cause |

Mark as **not duplicate** if:
- Similar area but different specific problem
- Same feature, different perspective or scope
- Previous issue was resolved and this is a regression

### Step 5: Output

#### Duplicate Found

```
Duplicate Found

Original: #123 - "title" (URL)
State: Open / Closed
Evidence:
  - Same error message "XXX" reported
  - Identical reproduction steps (do A then B)
  - Same component/file involved

Recommended Action:
  - Add duplicate label
  - Consider closing this issue
```

#### Related Items Found (not duplicate but related)

```
Related Items Found

Related Issues:
  - #456 - "title" (URL) — different bug in the same module
  - #789 - "title" (URL) — similar feature request, different scope

Related PRs:
  - #101 - "title" (URL) — Open, fix in progress for this issue
  - #102 - "title" (URL) — Merged, relevant prior fix
```

#### No Duplicates Found

```
No Duplicates Found

Search Summary:
  - Issues searched: N
  - Issues examined in detail: M
  - Assessment: appears to be a new issue

Suggested labels: bug / feature-request / question / etc.
```
