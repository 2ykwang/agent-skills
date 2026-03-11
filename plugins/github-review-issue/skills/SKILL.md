---
name: github-review-issue
version: 0.1.0
category: productivity
description: "Analyze a GitHub issue and provide a structured summary with next-action assessment."
argument-hint: "<issue-number or URL>"
---

# GitHub Issue Reviewer

Analyze a GitHub issue and produce a structured summary.

## Use this skill when

- Understanding what an issue is about before working on it
- Summarizing a long issue thread with many comments
- Assessing what action is needed to move an issue forward

## Do not use this skill when

- The user wants to create or edit an issue
- The user wants to check for duplicate issues (use github-review-check-duplicate)
- The user wants a PR review (use github-review-pr)

## Instructions

### Step 1: Parse Input

`$ARGUMENTS` is an issue number or GitHub URL.

- URL (e.g., `https://github.com/owner/repo/issues/123`): extract `owner/repo` and issue number, use `-R owner/repo`
- Number only: use the current repository

### Step 2: Fetch Data

```bash
gh issue view <number> [-R owner/repo] --json title,body,state,labels,comments,author,createdAt,assignees,milestone
```

### Step 3: Analyze and Report

#### Issue Summary
- Title, state (open/closed), author, created date
- Labels and milestone
- Assignees

#### Problem Analysis
- Core issue summary
- Reproduction steps or environment info (if available)
- Related code or error messages (if available)

#### Comment Summary
- Key discussion points
- Proposed solutions
- Current progress

#### Next Action
Assess what is needed for this issue to move forward:
- Missing reproduction info or environment details
- Needs assignee
- Related PR already in progress
- Stale — no activity for an extended period
