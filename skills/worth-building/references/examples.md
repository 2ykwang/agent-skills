# Worked examples

Each example shows the same shape in a different domain: a startable plan + a triggered skip + one forcing constraint. The **transition rule** on the last line is what lets the reader take away the shape, not the recipe. (One low-stakes example lives in the SKILL.md body.)

## 1. High-stakes, data (full path)

**Request:** "I want to dedupe customer records before import. Should I build a proper matching service?"

**Right-sized answer (touches customer data → full analysis at the stakes gate):**

> ## Recommendation
> - **Right-sized shape:** one-off script: normalize email+phone → group by that pair → keep the most recently updated row.
> - **Why this level:** the import is a one-off (not a recurring need, low certainty a service is ever needed), and exact match after normalization covers most of it. A fuzzy matching service is speculative complexity until you see the miss rate.
>
> ## How to build it (PoC)
> Load the records, normalize email and phone, group by that pair, and keep only the most recently updated row in each group. Export what's kept and what's dropped to separate files so a human eyeballs the drops before committing.
>
> ## Deliberately cut
> - Fuzzy name/address matching: add if the eyeball check shows real dupes slipping past exact match.
> - Reusable service/API: add if this stops being one-off and dedup becomes a recurring pipeline step.
>
> ## Upgrade triggers
> - Eyeball miss rate > a few % → introduce fuzzy matching.
> - A second team asks for the same dedup → promote the script to a shared service.

Note the shape: a startable plan, a skip with a trigger, and one forcing constraint (customer data → a human-review check step is not optional).

**Transition rule:** one-off task + human-review step + attached trigger. Right-sizing that touches data has all three, regardless of scale.

## 2. Non-software, doc/process (low-to-mid stakes)

**Request:** "Team onboarding is different every time. Should I build an onboarding automation system?"

**Right-sized answer (doubt the premise first: is the real problem the lack of automation?):**

> ## Recommendation
> - **Right-sized shape:** one checklist doc (wiki/markdown). A new hire makes a copy and checks off items.
> - **Why this level:** onboarding frequency is low (1-2/month), and the pain is "different every time" — whose cause isn't missing automation but a **missing standard**. An automation system is speculative complexity until the procedure sets; stale automation repeats the wrong procedure with confidence.
>
> ## How to build it (PoC)
> List what was actually done in the last 3 onboardings, turn it into check items in order, and attach an owner and a link to each. A human runs one copy and feeds missing steps back into the doc as they surface.
>
> ## Deliberately cut
> - Auto account provisioning / ticket creation: add when onboarding passes ~5/month or the procedure stabilizes.
> - Progress dashboard: add when several onboardings overlap and tracking breaks down.
>
> ## Upgrade triggers
> - The checklist keeps going stale from not being updated → promote to a tool with ownership.
> - More than half the steps measure as manual repetition → automate those steps first.

**Transition rule:** a process problem is usually a missing standard, not a missing tool. Set the standard in a doc first; automate when repetition shows up in measurement. "Lowest rung that holds" applies the same even when it isn't software.
