# commit-fixup edge cases

## One file's changes belong to several commits

`git add -p` is interactive and unusable in an automated environment. Split the hunks into patch files
and stage them:

```bash
git diff <file> > /tmp/all.patch
# split the patch by hunk into one patch file per target commit (manual edit)
git apply --cached /tmp/hunks-for-commit-A.patch
git commit --fixup=<commit-A>
git apply --cached /tmp/hunks-for-commit-B.patch
git commit --fixup=<commit-B>
```

Don't force it when the split is unclear. Sending the whole file to its last-toucher commit is safer,
and the history loss is small.

## Pushed branch, user wants to proceed anyway

Run the rebase the same way, but let the user do the push. Never run a force-push for them. Mention
`--force-with-lease` as guidance only.

## Conflict during the rebase

With the last-toucher rule there shouldn't be conflicts. A conflict means the mapping was wrong (fixup
into an earlier commit), or fixups on the same file created an ordering tangle. Run `git rebase --abort`
and review the mapping again. Forcing a resolution makes the lossless check meaningless.
If the state still looks wrong after aborting, `git reset --hard <branch>-fixup-backup` is the full recovery.

## Slow or failing commit hooks

Pre-commit hooks run on every fixup commit. A hook failure signals a code problem — don't work around it,
stop and report. Use `--no-verify` only when the user explicitly allows it.
