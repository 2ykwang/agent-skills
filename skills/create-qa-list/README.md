# create-qa-list

Turns code, a spec, a PR, or the current conversation into a QA test-case list a non-developer can read and run — exported as CSV, an HTML report, or both.

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install create-qa-list@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill create-qa-list
```

## When to use

- Need QA test cases, a test plan, or a QA checklist a non-developer can run
- Want cases exported as CSV (for a test tool) or a shareable HTML report
- The feature was just built or discussed here — the conversation is valid input

## Usage

```
# From the current conversation
/create-qa-list

# From a PR, file, or spec
/create-qa-list https://github.com/org/repo/pull/42
```

Works step by step — confirms scope, categories, and a case outline with you before writing full rows, so a 30-row list isn't built on a wrong assumption.

## How it works

1. **Scope** — identifies the target feature; confirms what's in, what's out, and which platform/role.
2. **Categories & priority** — agrees how cases are grouped and graded (P1–P3).
3. **Outline** — shares one-line case titles first, so gaps are cheap to catch.
4. **Export** — CSV, HTML, or both.

## Output

Test cases written in behavior-and-scenario language — what the user does and what they see, with no code symbols. CSV for import, or an HTML report with a built-in "Download CSV" button.

## Requirements

- `python3` (standard library only)

## Notes

- Every case rests on verified behavior; anything unconfirmed is flagged needs-confirmation, not guessed.
- Not for writing or running automated test code (pytest/jest), code review, or test-strategy docs.
