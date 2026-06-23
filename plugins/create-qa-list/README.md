# create-qa-list

Turn code, specs, a PR, or the current conversation into a QA test-case list a non-developer can read and run, exported as CSV, a shareable HTML report, or both. Trigger when the user wants QA test cases, a test plan, a QA checklist, or a test-case CSV/HTML (e.g. "write test cases for this", "make a QA list"). Output uses behavior-and-scenario language, never code symbols like function names or file paths. Not for writing or running automated test code (pytest/jest), code review, or test-strategy docs.

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

---

> Auto-generated from [skills/create-qa-list](../../skills/create-qa-list).
