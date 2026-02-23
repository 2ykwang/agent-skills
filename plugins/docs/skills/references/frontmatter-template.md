# Document Frontmatter Specification

All documents managed by this skill must include the following frontmatter.

## Template

```yaml
---
title: <document title>
category: <category>
created: <YYYY-MM-DD>
updated: <YYYY-MM-DD>
related: []
code_refs: []
---
```

## Field Description

| Field | Required | Description |
|-------|----------|-------------|
| `title` | O | Document title (the topic entered by user) |
| `category` | O | Document category. Must match the directory name |
| `created` | O | Creation date (YYYY-MM-DD) |
| `updated` | O | Last updated date (YYYY-MM-DD). Must be updated on every modification |
| `related` | - | Array of related document slugs. e.g. `["auth-flow", "session-management"]` |
| `code_refs` | - | Array of code reference file paths (project root relative). e.g. `["src/auth/handler.py", "src/middleware/auth.py"]` |

## Category Seeds (suggested when project has no documents)

| Category | Purpose |
|----------|---------|
| `architecture` | System design, architecture decisions |
| `guides` | How-to, procedural guides |
| `decisions` | ADR (Architecture Decision Records) |
| `references` | API contracts, data models, interface definitions |

If the project already has categories, use those first.

## Code Reference Usage

**frontmatter** — record file paths only:
```yaml
code_refs:
  - "src/auth/handler.py"
  - "src/middleware/auth.py"
  - "src/models/user.py"
```

**body** — inline reference as markdown links:
```markdown
[authenticate](src/auth/handler.py) validates the JWT token.
The auth middleware is implemented in [AuthMiddleware](src/middleware/auth.py).
```

- Project root relative paths
