**English** | [한국어](README.ko.md)

# instruction-eval

Change one condition an agent runs under, such as an instruction, a reference doc, a hook, or a permission, then run the same prompts before and after, several times each, and see what actually changes. Produces an HTML report with both arms' answers side by side.

Built on Claude Code. Both arms run as `claude -p` subprocesses.

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install instruction-eval@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill instruction-eval
```

## When to use

- **Deciding whether to add a rule, and you want evidence it does anything**
  - `/instruction-eval I added "comments must be self-contained" to CLAUDE.md. Check whether answers actually change with and without it.`
- **You want to delete an existing rule but have no basis for it**
  - `/instruction-eval Drop the "read every related file before editing" rule from CLAUDE.md and check whether removing it actually breaks anything.`
- **The same rule written two different ways, and you don't know which wording lands**
  - `/instruction-eval Compare "keep answers brief" against "lead with the conclusion, then at most three lines of reasoning" and see which one gets followed.`
- **You placed a reference doc and don't know whether the agent reads it**
  - `/instruction-eval I put docs/api-conventions.md in the repo. Check whether the agent finds and cites it, compared to it not being there.`

Not for application code changes or anything automated tests already cover.

## Usage

```
/instruction-eval <what to compare against what>
```

Give it the axis and it builds both conditions, writes the prompt set, picks the run count, and gets your approval before anything runs.

## How it works

1. **Design.** Picks the axis, meaning what's present in one arm and absent in the other, builds two working directories, then verifies with `diff -rq` that nothing else differs.
2. **Approve.** Shows the axis, the `diff -rq` output, the full prompt set, n, and the model. Nothing runs without your approval.
3. **Run.** `run_ab.py` runs `claude -p` in both directories, n times per prompt, in parallel so neither arm gets a prompt-cache advantage.
4. **Report.** `render_report.py` renders a single-file HTML report: both answers side by side, plus medians and observed ranges for duration, turns, and output tokens.
5. **Interpret.** You read the answers, then write an `insights.json` that gets merged into the report and kept visually distinct from the measured data.

The report only carries three metrics. Input tokens and cost are dominated by prompt caching and can move opposite to actual work, so they're excluded. Rows where the two arms' observed ranges overlap get flagged, because that delta may be run-to-run variance rather than an effect.

## Requirements

- Claude Code CLI (`claude -p` is run as a subprocess)
- `python3`
