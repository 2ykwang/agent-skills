---
name: instruction-eval
version: 0.5.1
category: productivity
description: "Change one condition an agent runs under (instruction text, the reference material instructions point at, MCP tools and permissions, hooks, skill files), then run the same prompts before and after, several times each, to see what actually changes. Produces an HTML report showing both arms' answers side by side. Use when deciding whether to add a rule, when you need evidence that an existing rule can be deleted, when picking between two wordings of the same rule, or when checking whether material you placed is actually being read. Triggers on 'does this rule do anything', 'compare before and after adding this', 'can I drop this', 'difference with and without this', 'run an A/B'. Not for application code changes or anything automated tests already verify. Built on Claude Code: it spawns `claude -p` subprocesses to run both arms."
argument-hint: "<what to compare against what>"
---

# Condition A/B

Change one condition an agent runs under, run the same prompts before and after,
and show the difference.

The conditions surrounding an agent have no verification. You can read code and
tests will catch a regression, but a few lines added to instructions or a
reference doc dropped in a directory only ever get judged on whether they sound
reasonable. Even the person who put them there has no idea whether they change
behavior. This skill replaces that guess with an observation.

This runs on Claude Code. Both arms execute as `claude -p` subprocesses, so the
CLI has to be available.

## Who writes what

The report holds content from two sources, visually separated in the HTML. Never
hand-write what the script produces, since transcribing only introduces errors.

| Automatic (scripts) | LLM (`insights.json`) |
|---|---|
| Experiment setup: n, model, both directory paths | What you changed |
| Prompt text | The claim about what changes |
| Answer text (every arm, every rep) | Differences observed per prompt |
| Metric medians and deltas | Metric interpretation |
| Run anomalies (errors, permission denials) | Conclusion |

## Procedure

### 1. Design and build the conditions

**Pick the axis first.** What you compare against what determines everything else.
Only what the user mentioned is a candidate, and even when it reads as obvious you
confirm it in step 2.

Anything can be the axis: instruction text, reference material instructions point
at, MCP tools and permissions, hooks, skill files. The script only sees two
directories, so all of these get handled identically.

`baseline` is the working directory in the before state, `variant` the after state.

**The purpose decides the direction.**

| | Verifying an addition | Building a case for deletion |
|---|---|---|
| baseline | axis absent | axis present (status quo) |
| variant | axis present | axis absent |
| What you watch | does it do what the axis asks | does the failure it prevented show up |

Deletion is the more common need. Instructions only grow in one direction and
nothing ever makes the case for removing them, while an ineffective instruction
still rides along on every request, spending context and diluting the signal of the
instructions that do work. Judge deletion asymmetrically, though. The bar is not
"delete when there's no evidence of effect" but **"delete only when removing it is
confirmed to produce no failure."** A symmetric bar at small sample sizes will
delete rules on noise.

**The situation decides how you build them.** Comparing two commits means
`git worktree`, uncommitted changes mean copying files into a worktree, and
candidate wording not yet written to a file means creating a temp file. The script
stays out of this, so use whatever fits.

**Always verify after building.**

```bash
diff -rq <baseline> <variant>
```

**If anything other than the intended axis differs, the A/B doesn't hold.** That one
line catches everything below. (With worktrees `.git` shows up as different, but it's
a pointer file, so ignore it.)

- `git worktree` only brings tracked files. Anything outside version control, such as
  build output or reference material fetched locally, doesn't come along. **If the
  axis is an instruction whose effect depends on such files, reproduce them in both
  arms.** Skip that and neither arm finds anything, producing a false "no effect"
  conclusion. If that material *is* the axis, actually delete it on one side.
- A session-start hook doing network or build work puts its latency into the duration
  numbers. Disabling it identically in both arms is safer.
- An "absent file" condition can't be faked with an empty file. The path still exists
  and turns up in searches, so delete it for real.

**Change one axis at a time.** Conditions interfere with each other, and changing two
leaves you unable to tell which one produced the effect.

**Build the prompt set.**

```json
[
 {"id": "on-1", "kind": "on-target", "prompt": "..."},
 {"id": "off-1", "kind": "off-target", "prompt": "..."}
]
```

**Include at least one off-target prompt.** The person who wrote the instruction picks
the prompts, so a set of questions the instruction happens to handle well makes variant
win every time. That's an incentive problem rather than a tool defect, and mixing in
unrelated questions is the only fix. The more interesting question is usually whether
the instruction breaks other work, and only off-target prompts show that.

Write prompts as concrete sentences a real user would send. Something abstract like
"check the config" produces vague answers on both sides and no visible difference.

**Pick n.** Minimum 3, or 5 and up if it's going to drive a decision. Time and cost
scale with n. **Never use n=1.** Agent runs vary by tens of percent in coefficient of
variation even under identical conditions, so a single-run comparison can't separate
the axis's effect from noise. Even n=5 falls short of statistical significance. **At
any scale this tool produces a directional estimate, not a settled effect size.** Word
the report that way.

### 2. Show everything and get approval before running

**Experiments are slow and irreversible.** Rather than burning 30 minutes on a wrong
setup, show what you built as-is and get approval. Fixing a directory when something
turns out wrong here costs far less than one run.

Show these. Don't summarize, present exactly what you built.

| Item | Content |
|---|---|
| Axis | What's missing from baseline, what's present in variant. Path or `file:line` |
| Held equal | Anything axis-related you deliberately controlled. `diff -rq` only reports differences, so it won't appear there |
| `diff -rq` output | Actual output, unprocessed |
| Prompts | Full text, with on/off-target labels |
| n, model, total runs | |
| Claim | The user's, verbatim. "None" if they didn't make one |

Don't run without approval.

### 3. Run

```bash
python <skill-path>/scripts/run_ab.py \
  --baseline <directory> --variant <directory> \
  --prompts <prompts.json> --work <results directory> \
  --n <N> --model <current session model ID>
```

Pass the current session model ID to `--model`. Omit it and the subprocess uses the
user's default model, which makes the results diverge from what the user actually
experiences.

It takes a while, so run it in the background.

### 4. Build the report

Render without insights first and read the answers in the HTML.

```bash
python <skill-path>/scripts/render_report.py --work <results directory>
```

Reading `runs/*.json` directly works too, but the HTML puts both arms side by side,
which is faster.

After reading, write `insights.json`. Every key is optional, and missing ones show as
"not written" in the report.

```json
{
 "title": "Report title",
 "change": "What you changed",
 "arms": {"baseline": "no rule", "variant": "rule added"},
 "claim": "The claim about what changes (\"none\" if there isn't one)",
 "prompts": {"on-1": "difference observed on this prompt"},
 "metrics": "Metric interpretation",
 "conclusion": "Conclusion"
}
```

**Always fill in `arms`.** Which side holds the axis flips depending on purpose, so
without labels a reader can't tell which column is which. It's pinned above every tab
alongside `change`.

```bash
python <skill-path>/scripts/render_report.py --work <results directory> --insights insights.json
```

Pick a grading method in this order.

1. **If code can count it, use code.** Format compliance, presence of a specific string,
   citation count, lint passing, and anything else mechanically checkable is fastest and
   most reproducible as a script.
2. **If it needs judgment, read the answers yourself.** An instruction A/B has only a
   handful of prompts, so reading them isn't expensive, and this tool's report puts both
   answers side by side for exactly that.
3. **Use an LLM grader only when there's too much to read yourself.** If you do, give it
   a per-item rubric rather than a prose criterion, and run it with the two answers in
   both presentation orders. Grading models favor the first answer and the longer one, so
   a fixed order bakes that bias into the result.

When reading answers yourself, watch for the tendency to reward confident wrong answers.
People rate a wrong answer written decisively above a correct one written carefully,
which is why the first item below matters. Look at the evidence, not the tone.

What to look for:

- Did **the arm without the axis** say it didn't know, or give a wrong answer? Those are
  completely different failures. If the claim names one and the measurement shows the
  other, **the claim is what needs fixing.**
- Does **the arm with the axis** cite its source? Saying the right thing without citation
  may be coincidence.
- On off-target prompts, did the arm with the axis do unnecessary searching?

Which arm holds the axis flips depending on purpose, so read by **which side has the
axis** rather than by the slot names `baseline` and `variant`.

If observations contradict the original claim, write that down. Sometimes the biggest
output is that the claim was wrong, which means the tool did its job.

## Rules for reading metrics

**Only three metrics are usable for comparison: duration, turn count, and output
tokens.** Input tokens and cost are dominated by prompt caching and can move opposite to
actual work, so the report excludes them.

**Don't read the delta when the ranges overlap.** The report shows each arm's observed
min and max and flags overlapping rows. Overlap means each arm falls inside the other's
own spread, so the difference may be run-to-run variance rather than an effect.

**Don't interpret a metric alone.** Whether increased duration and output means worse
cost or more complete answers isn't decidable from numbers. Each row only means something
when read against the answers.

**Don't average across prompts.** The same instruction can push in opposite directions on
different prompts, and averaging cancels them into a false "no difference".

**Don't decide in advance which way a metric should move.** Adding instructions can mean
more to read and higher cost, or a search that ends earlier and lower cost. If the
direction contradicts your expectation, record that as an observation.

**Watch the "run anomalies" warning.** When errors or permission denials cluster in one
arm, that time is baked into its metrics and the two arms aren't equivalent.

## Environment

Runs `claude -p` as a subprocess. Unusable where the Claude Code CLI isn't available.
