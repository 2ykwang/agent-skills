# ralph-loop-template

Generates an iterable checklist PROMPT file for [Ralph Loop](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum) from a plan file or the current conversation.

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

## When to use

- Have an implementation plan and want to run it phase-by-phase with automated verification
- Need to split a large task into Ralph Loop iterations
- Want a ready-to-run `/ralph-loop` command with the right flags

## Usage

```
# From a plan file
/ralph-loop-template PLAN.md

# Auto-detect a plan file (PLAN.md, TODO.md, …) or use the current conversation
/ralph-loop-template
```

## How it works

1. Extracts goals, non-goals, and phases from the plan.
2. Detects the project's build/test/lint commands.
3. Splits the plan into iteration-sized phases.
4. Generates `PROMPT-<name>.md` and a ready-to-copy `/ralph-loop` command.

## Output

```
### Generated File
`PROMPT-auth-refactor.md`

### Ralph Loop Execution Command
/ralph-loop "Read PROMPT-auth-refactor.md and implement the next unchecked phase." --max-iterations 7 --completion-promise "AUTH REFACTOR DONE"
```

## Requirements

- [ralph-wiggum](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum) plugin
