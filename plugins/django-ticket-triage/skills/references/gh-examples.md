# GitHub CLI Examples for Django

Use the `gh` CLI for all GitHub-related information. **DO NOT use WebFetch for GitHub URLs.**

## Search PRs

```bash
# Search PRs mentioning ticket number
gh search prs "Fixed #<ticket_id>" --repo django/django --limit 10
gh search prs "#<ticket_id>" --repo django/django --limit 10

# Search by Trac ticket URL
gh search prs "code.djangoproject.com/ticket/<ticket_id>" --repo django/django --limit 10
```

## View PR Details

```bash
# View PR details
gh pr view <pr_number> --repo django/django
gh pr view <pr_number> --repo django/django --json title,state,body,comments

# View PR diff
gh pr diff <pr_number> --repo django/django

# View PR comments and reviews
gh api repos/django/django/pulls/<pr_number>/comments
gh api repos/django/django/pulls/<pr_number>/reviews
```

## Issues

```bash
gh search issues "<query>" --repo django/django
```

## Commits

```bash
# View commit details (for forks, replace django/django with owner/repo)
gh api repos/django/django/commits/<sha>
gh api repos/<fork_owner>/django/commits/<sha>

# View commits in a PR
gh api repos/django/django/pulls/<pr_number>/commits

# View file content at specific commit
gh api repos/django/django/contents/<path>?ref=<sha>

# Compare branches/commits
gh api repos/django/django/compare/<base>...<head>
```
