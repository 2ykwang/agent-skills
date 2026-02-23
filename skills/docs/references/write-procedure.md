# write Procedure

## Step 1: Bootstrap Check

1. **Glob** to check if `docs/generated/` directory exists (`docs/generated/**` pattern)
2. If it does not exist:
   - Ask user: "`docs/generated/` directory does not exist. Create it?"
   - On approval, create `docs/generated/` directory
   - Create empty INDEX.md:
     ```markdown
     # Documentation Index

     > Last updated: YYYY-MM-DD
     ```

## Step 2: Duplicate Document Check

Search for existing documents on the same topic.

1. Convert topic to kebab-case slug (translate non-English to English)
   - e.g. "auth flow design" → `auth-flow-design`
2. **Glob**: `docs/generated/**/<slug>.md` or similar patterns for filename matching
3. **Grep**: Collect frontmatter `title:` patterns from `docs/generated/` path
4. Compare topic keywords against existing titles to detect duplicates

**Based on match results:**
- **1 match**: "Found existing document: `<path>`. Update it or create a new one?"
- **2+ matches**: Present candidate list and ask user to choose
- **No match**: Proceed to create new document

## Step 3: Context Gathering

Gather context needed for document writing.

**When code-path argument is provided:**
- **Read** the code at the given path
- If it's a directory, use **Glob** to find key files, then read only essential ones

**When code-path argument is not provided:**
- Use current working context (conversation context, recent git diff, etc.)
- May ask user for related code location

**Search for related existing documents:**
- **Read** `docs/generated/INDEX.md` to understand category structure and document list
- **Grep** frontmatter of existing documents for topic-related keywords
- Record related documents as candidates for the `related` field

## Step 4: Category Decision

1. **Glob** subdirectories under `docs/generated/` to identify existing categories
2. Match the most suitable category for the topic
3. If no suitable category exists:
   - Suggest a new category (e.g. "How about putting this document in the `architecture` category?")
   - Apply after user confirmation
4. If the project has no documents at all, refer to category seeds in `references/frontmatter-template.md`

## Step 5: Write Document

1. **Read** `references/frontmatter-template.md` for frontmatter specification
2. Determine file path: `docs/generated/<category>/<slug>.md`
3. Create the category directory if it does not exist
4. Generate frontmatter:
   - `title`: the topic entered by user
   - `category`: category decided in Step 4
   - `created`: today's date
   - `updated`: today's date
   - `related`: related document slugs found in Step 3
   - `code_refs`: related code file paths (project root relative)
5. Body writing principles:
   - Focus on **design intent and how things work**
   - Use `[symbol](file-path)` reference pointers instead of code blocks
   - Include code examples only when absolutely necessary (e.g. usage examples)
   - Use a scannable structure (headings, lists, tables)

## Step 6: Update INDEX.md

1. **Read** `docs/generated/INDEX.md`
2. Add new document entry to the appropriate category section:
   ```markdown
   | [document title](<category>/<slug>.md) | YYYY-MM-DD |
   ```
3. Create the category section if it does not exist
4. Update `Last updated` date
5. If related documents are recorded in the `related` field:
   - Add the current document slug to the `related` field of those documents (**Edit**)

## Step 7: Result Summary

After write/update is complete, output:

```
✅ Document written

- Path: docs/generated/<category>/<slug>.md
- Category: <category>
- Code references: N
- Related documents: [list]
```
