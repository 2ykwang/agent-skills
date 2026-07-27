**English** | [한국어](README.ko.md)

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

1. Finds the plan — the file you passed, an auto-detected one (`PLAN.md`, `TODO.md`, `PRD.md`, …), or the current conversation.
2. Detects the project's build/test/lint commands from `CLAUDE.md`, `.cursorrules`, `AGENTS.md`, or the build files, and chains them into one verification command.
3. Extracts goals, non-goals, and phases. Non-goals matter — they're what keeps the loop from inventing work, so it infers extras (out-of-scope refactoring, unrequested test/doc changes) on top of what the plan excludes.
4. Splits the plan into iteration-sized phases. One iteration runs exactly one phase, and each phase has to be small enough to pass verification on its own.
5. Generates `PROMPT-<name>.md` and a ready-to-copy `/ralph-loop` command, with `--max-iterations` set to the phase count plus two — one spare for a failed verification retry, one for the final completion output.

## Output

```
### Generated File
`PROMPT-auth-refactor.md`

### Ralph Loop Execution Command
/ralph-loop "Read PROMPT-auth-refactor.md and implement the next unchecked phase." --max-iterations 7 --completion-promise "AUTH REFACTOR DONE"
```

Review the generated PROMPT file before running it — the verification command and the phase split are the two things worth a second look. The loop repeats that file verbatim every iteration, so a wrong verification command is wrong on every pass.

## Requirements

- [ralph-wiggum](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum) plugin, which provides `/ralph-loop`

## Notes

- Invoke it explicitly. Unlike the other skills here, this one never triggers on its own.
- Completion criteria must be mechanically verifiable — a command that exits 0. "Works well" and "looks clean" don't qualify.
