# check Procedure

## Step 1: Document Root Check

1. **Glob** `docs/generated/**/*.md` pattern to check if documents exist
2. If no documents found:
   ```
   📭 No documents found in docs/generated/.
   Create your first document with `/docs write <topic>`.
   ```
   Stop.

## Step 2: Collect Documents

1. **Glob**: `docs/generated/**/*.md` (exclude INDEX.md)
2. **Read** frontmatter of each document to collect:
   - `title`, `updated`, `code_refs`, `related`

## Step 3: Run Checks

Run the following checks on each document.

### 3-1. Stale Detection

- Documents with `updated` date exceeding 90 days from today are classified as stale

### 3-2. Broken Code References

- Extract file paths from each item in the `code_refs` array
- **Glob** to check if the file exists in the project
- Record non-existent file paths as broken references

### 3-3. Broken Document Links

- For each slug in the `related` array
- **Glob**: check if `docs/generated/**/<slug>.md` exists
- Record non-existent slugs as broken links

### 3-4. Orphan Documents

- **Read** `docs/generated/INDEX.md`
- Extract the list of linked document paths from INDEX.md content
- Classify documents not linked in INDEX.md as orphans

## Step 4: Report Output

Output check results in the following format:

```
📋 Document Status Report

⚠️  Stale (90+ days since update): N
  - docs/generated/path/file.md (last updated: YYYY-MM-DD, N days ago)

❌ Broken code references: N
  - docs/generated/path/file.md → src/old/file.py (file not found)

🔗 Broken document links: N
  - docs/generated/path/file.md → related: slug (document not found)

📄 Not in index: N
  - docs/generated/path/file.md

✅ Healthy: N
```

Omit sections with 0 items.

## Step 5: INDEX.md Update Proposal

If issues are found or there are unindexed documents:

1. Ask the user: "Update INDEX.md?"
2. On approval:
   - Regenerate INDEX.md based on all document frontmatter
   - Group by category (based on directory structure)
   - Mark stale documents with `⚠️ stale` in the status column
   - Update `Last updated` date to today

**INDEX.md format:**

```markdown
# Documentation Index

> Last updated: YYYY-MM-DD

## <category> (N)

| Document | Last Updated | Status |
|----------|--------------|--------|
| [title](<category>/<slug>.md) | YYYY-MM-DD | ✅ / ⚠️ stale |
```
