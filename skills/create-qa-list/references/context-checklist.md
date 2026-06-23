# Context self-check

Run before each step. QA-list failures happen silently: a confident 30-row CSV built on a wrong scope assumption "looks thorough" but tests the wrong thing. This check surfaces missing context *before* you spend effort.

If there's a question you can't answer, that's the question to ask the user — don't fill the blank with a guess.

## Before Step 1 (scope)

- **What feature/behavior is under QA?** Can you name it in one sentence from code/spec/conversation, or are you guessing among several candidates?
- **What changed / is new?** QA usually focuses on new or changed behavior. Do you know what's new vs. existing?
- **Who uses it, on which platform?** Web/app/tablet, login role, account type, lineup — this changes which cases exist.
- **Is there an authoritative source?** A spec, PRD, or ticket beats your inference. Did the user point at one, or do you need to ask if one exists?
- **What's explicitly out of scope?** Adjacent features that look related but the user doesn't want tested.

## Before Step 2 (categories & priority)

- **Do the categories come from this feature, or are they a generic list?** Good categories mirror the feature's real surface (input validation, visibility conditions, rewards, state transitions, etc.). Generic buckets ("UI / Feature / Misc") tell the QA tester nothing.
- **Are the priority rules meaningful for this feature?** What's worst if it breaks here (money, data loss, flow blocked)? That's P1.

## Before Step 3 (draft list)

- **Negative and edge cases, not just the happy path.** No auth, another user's resource, empty/null, boundaries (0/negative/max), duplicates, concurrent actions. Which of these apply?
- **Cross-domain effects.** Does one action ripple into another domain (reward → log → notification)? Each ripple is a case.
- **State permutations.** First use vs. reuse, before vs. after a threshold, mode A vs. mode B.

## Before Build

- **Does every expected result rest on real code/spec, not a guess?** (Rule 2.) For each row, can you point to where you verified this behavior? If it's a guess, confirm from code, ask the user, or drop the case. A plausible-but-wrong expected result is the worst output this skill can produce.
- **Does every case have an observable expected result?** If you can't say *what the tester will see*, the case isn't ready.
- **Can a non-developer run each case from the app and the row text alone** — no code, no explanation from you?
