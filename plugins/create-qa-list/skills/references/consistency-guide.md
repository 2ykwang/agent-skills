# Consistency guide

The reader is a **non-developer QA tester**. They run the product and watch what happens. They don't read code. Everything below serves one goal: every row reads the same way and that person can run it. Read all of this before Build.

## Columns (default)

Unless you agreed otherwise with the user in Step 2, use these seven columns in this order.

| Column | What goes in it | Rule |
|--------|-----------------|------|
| `TC_ID` | `TC-001`, `TC-002` … | Sequential, 3-digit zero-pad. Never reused. |
| `Category` | Feature area | Must be one of the set agreed in Step 2. Lets the list be grouped. |
| `Scenario` | One line: what's being verified | Noun phrase or short sentence. The case should be graspable from this alone. |
| `Preconditions` | State to set up before the test | Account type, day/elapsed time, last-saved state, platform. Concrete values, not "appropriate setup". |
| `Steps` | Steps the tester performs | Numbered, imperative, product language ("add item → apply coupon → pay"). Not API calls. |
| `Expected Result` | What the tester should see | Observable on screen. The pass/fail baseline. |
| `Priority` | `P1` / `P2` / `P3` | Per the rubric below. |

Keep the column set **identical across every row**. If a column the feature needs is added (e.g. `Target device`), add it to every row, not some.

Note: the HTML report depends by name on `TC_ID`, `Category`, `Priority` (groups, badges, summary) and `Steps`, `Expected Result` (multi-line render). **Adding** columns is safe, but removing or renaming these five breaks the HTML (CSV is unaffected). That's why the build script rejects a column set missing `TC_ID`, `Category`, or `Priority`.

## Non-developer tone — the most-often-broken rule

Translate every technical fact into observable behavior. The tester verifies on screen, so write what they'll see.

**Example 1**
- Bad: `update_order_status doesn't set completed_at`
- Good: `After paying, the order still isn't shown as complete`

**Example 2**
- Bad: `returns BASIC coupon when grade != VIP`
- Good: `A non-VIP account sees only the basic coupons`

**Example 3**
- Bad: `reward_point=0 when order_history is missing`
- Good: `Points aren't earned when the order didn't go through the normal path`

Never output: function/method names, variable names, file paths, table/column names, enum constant names, or an HTTP status code as the *primary* expected result (a non-developer doesn't see "400" — they see "the save is blocked and a message appears"; add the code in parentheses only when QA explicitly tracks it).

A good expected result is **observable and concrete**. "Works correctly" is not a result — write what the tester sees: the message, the state change, the screen, the number.

## Categories

Categories mirror the feature's real surface so the tester can work one area at a time. Derive them from the scope. Examples of the *shape* (not a menu to copy verbatim):

- Input validation, visibility/display conditions, rewards/credits, state transitions, data persistence, cross-domain effects.

Avoid generic buckets like "Feature / UI / Misc" — they don't help the tester batch their work.

## Priority rubric (default — tune and confirm in Step 2)

Apply in **decision order**: top to bottom, take the first grade that matches. That keeps rows consistent instead of graded by gut.

1. **P1** — breaks money, data, or auth/security, or blocks a core flow. Decision test: *"If this ships broken, is it a rollback or emergency hotfix?"* If yes → P1.
2. **P2** — behavior is wrong but the product still works: there's a workaround, only some users/conditions hit it, or it can wait for the next regular release.
3. **P3** — the feature works; only appearance, copy, or very rare combinations are affected.

| Grade | One-line test | Typical cases |
|-------|---------------|---------------|
| **P1** | Rollback/hotfix if broken? | Reward double-pay or non-pay, payment/auth, data loss, core flow blocked, IDOR (another user's resource), validation bypass that saves bad data |
| **P2** | Wrong but workable? | Wrong visibility conditions, ordering errors, completed state not preserved, edge-case validation |
| **P3** | Only cosmetic or rare? | Copy, minor layout, very rare combinations |

**Mistake to avoid: marking everything P1** ("it's all important"). If more than ~⅓ of cases are P1, re-filter with the rollback test — most will be P2. Reserve P1 for what truly blocks a release.

## Writing rules that keep rows consistent

- One case verifies **one behavior**. If the steps need "and also check…", split it into two cases.
- Preconditions use the same terms across rows (pick one phrasing for account type and reuse it).
- Steps and expected results are written from the **tester's** point of view, present tense, product language.
- A negative case states both the bad input *and* the expected defense ("save with a required item removed → save is blocked and a message appears").
- **Don't write an expected result you haven't verified.** Every expected result must reflect real code/spec behavior (SKILL.md Rule 2). If you're inferring what the code *should* do rather than what it *does*, confirm it or flag it to the user — don't export a guess as fact. A wrong expected result sends QA chasing a non-bug or passing a real one.
