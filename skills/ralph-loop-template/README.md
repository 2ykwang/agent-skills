# ralph-loop-template

Generates an iterable checklist PROMPT file for [Ralph Loop](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum) from a plan file or conversation context.

## When to use

- Have an implementation plan and want to execute it phase-by-phase with automated verification
- Need to split a large task into Ralph Loop iterations
- Want a ready-to-run `/ralph-loop` command with the right flags

## Usage

```
# Generate from a plan file
/ralph-loop-template PLAN.md

# Auto-detect plan file in project root (PLAN.md, TODO.md, etc.)
/ralph-loop-template

# Use the plan discussed in the current conversation
/ralph-loop-template
```

## How it works

1. Extracts goals, non-goals, and phases from the plan
2. Detects the project environment (build/test/lint commands)
3. Splits the plan into iteration-sized phases
4. Generates `PROMPT-{name}.md` and a ready-to-copy `/ralph-loop` execution command

## Output example

```
### Generated File
`PROMPT-auth-refactor.md`

### Ralph Loop Execution Command
/ralph-loop "Read PROMPT-auth-refactor.md and implement the next unchecked phase." --max-iterations 7 --completion-promise "AUTH REFACTOR DONE"
```

## Requirements

- [ralph-wiggum](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum) plugin

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install ralph-loop-template@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill ralph-loop-template
```
