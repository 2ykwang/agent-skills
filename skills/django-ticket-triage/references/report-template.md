# Triage Report Template

## Full Report Format

Save to `triage-reports/<ticket_id>.md`:

```markdown
# Triage Report: Ticket #<ticket_id>

**Generated**: <current date>
**Ticket URL**: https://code.djangoproject.com/ticket/<ticket_id>

## Summary

| Field | Value |
|-------|-------|
| Title | <summary> |
| Component | <component> |
| Version | <version> |
| Status | <status> |
| Triage Stage | <triage_stage> |
| Has Patch | <yes/no> |
| Reporter | <reporter> |
| Owner | <owner or "None"> |
| Created | <created date> |
| Last Edited | <last edited date> |


## Issue Description

<Detailed summary of the ticket content>

## Validity Assessment

### Ticket Type: <Bug Report / Feature Request / Documentation / Cleanup>

<For bugs>
- [ ] Reproduction steps provided
- [ ] Occurs on latest version
- [ ] Django's responsibility (not user code)
- [ ] Differs from documented/intended behavior
- [ ] Affects supported Django version
- [ ] Not a security issue

<For features>
- [ ] Useful to many users
- [ ] Aligns with Django philosophy
- [ ] Cannot be solved with third-party package
- [ ] No backwards compatibility issues
- [ ] Maintenance burden is acceptable

### Assessment Result

<Detailed validity assessment with rationale>

## Critical Analysis

Evaluate the ticket from a skeptical perspective:

### Potential Weaknesses
- <Issues with the ticket's argument, reproduction steps, or proposed solution>
- <Missing information or unclear requirements>
- <Edge cases not considered>

### Counter-arguments
- <Why this might NOT be a valid bug (e.g., intended behavior, user error)>
- <Why this feature might NOT be accepted (e.g., too niche, maintenance burden)>
- <Alternative interpretations of the problem>

### Questions to Consider
- <What additional information would strengthen/weaken this ticket?>
- <Are there simpler alternatives?>
- <What are the risks of implementing this?>

### Why This Ticket Might Be Rejected
- <Specific reasons why a Django maintainer might close this as wontfix/invalid>

## Duplicate Analysis

### Search Queries Used
1. `<query 1>` - <number> results
2. `<query 2>` - <number> results
3. `<query 3>` - <number> results

### Related Tickets Found

| Ticket | Title | Status | Relevance |
|--------|-------|--------|-----------|
| [#XXXX](https://code.djangoproject.com/ticket/XXXX) | <title> | <status> | <why related or not duplicate> |
| [#YYYY](https://code.djangoproject.com/ticket/YYYY) | <title> | <status> | <why related or not duplicate> |

### Duplicate Status: <Duplicate / Not Duplicate>

<Rationale>

## Related Resources

### GitHub PRs
| PR | Title | Status | Notes |
|----|-------|--------|-------|
| [#ZZZZ](https://github.com/django/django/pull/ZZZZ) | <title> | <open/merged/closed> | <notes> |

### Forum Discussions
| Topic | URL |
|-------|-----|
| <title> | [link](https://forum.djangoproject.com/t/<slug>/<id>) |

### Related Code
- `django/path/to/file.py:<line>` - <description>
- `tests/path/to/test.py:<line>` - <description>

## Contribution Notes

<Detailed notes for potential contributors>
- Fix approach suggestions
- Caveats and constraints from previous discussions
- Test requirements
- Documentation update needs
- Related areas that might be affected

## Recommendation

| Field | Value |
|-------|-------|
| Recommended Triage Stage | <stage> |
| Resolution (if applicable) | <resolution> |

### Rationale

<Detailed justification for the recommendation>
```

## Terminal Summary Format

After saving the file, output this brief summary:

```
## Triage Summary: #<ticket_id>

**<summary>**

Ticket: https://code.djangoproject.com/ticket/<ticket_id>

| | |
|-|-|
| Status | <status> / <triage_stage> |
| Duplicate | <Yes (see [#XXXX](https://code.djangoproject.com/ticket/XXXX)) / No> |
| Valid | <Yes / Needs info / No> |
| Has PR | <[#ZZZZ](https://github.com/django/django/pull/ZZZZ) / None> |

**Recommendation**: <triage_stage> - <one sentence rationale>

Full report saved to: `triage-reports/<ticket_id>.md`
```
