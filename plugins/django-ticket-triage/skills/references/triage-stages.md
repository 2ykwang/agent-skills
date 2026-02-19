# Django Triage Stage & Resolution Definitions

## Triage Stages

- **Unreviewed**: Not yet reviewed
- **Accepted**: Confirmed as valid ticket
- **Ready for checkin**: Review complete, waiting for merge
- **Someday/Maybe**: May be addressed eventually
- **Design decision needed**: Requires design decision

## Resolutions

- **fixed**: Fixed
- **duplicate**: Duplicate (specify original ticket number)
- **wontfix**: Decided not to fix
- **needsinfo**: Needs more information
- **invalid**: Not valid (not a bug, user error, etc.)
- **worksforme**: Cannot reproduce

## Recommended Triage Stage Decision

| Condition | Recommended Stage |
|-----------|-------------------|
| Valid bug, reproducible | **Accepted** |
| Reasonable feature request | **Accepted** |
| Needs more info (reproduction steps, version, etc.) | **needsinfo** |
| Duplicate of existing ticket | **duplicate** (link to original) |
| Outside Django scope or intended behavior | **wontfix** / **invalid** |
| Design decision required | **Design decision needed** |

## Duplicate Criteria

| Situation | Decision |
|-----------|----------|
| Same bug (same error, same reproduction steps) | **Duplicate** |
| Same feature request (different wording) | **Duplicate** |
| Same root cause (different symptoms but same cause) | **Duplicate** |
| Similar area but different specific issue | **Not duplicate** |
| Previous ticket was fixed, this is a regression | **Not duplicate** (new ticket) |
