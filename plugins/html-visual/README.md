# html-visual

Generates interactive single-file HTML visualizations — UI mockups, ERDs, flowcharts, data charts, presentations, and more.

## Installation

### Claude Code

```bash
claude plugin marketplace add 2ykwang/agent-skills
claude plugin install html-visual@2ykwang-agent-skills
```

### npx skills

```bash
npx skills add 2ykwang/agent-skills --skill html-visual
```

## When to use

- Need a UI mockup or wireframe
- Visualize a database schema as an ERD
- Map out business logic as a flowchart
- Create a data chart, architecture diagram, or dashboard
- Build a quick presentation from content

## Supported types

`mockup` · `wireframe` · `erd` · `flow` · `chart` · `slides` · `arch` · `dashboard` · `timeline` · `mindmap` · `kanban` · `table`

## Usage

```
# Explicit type
/html-visual mockup login page
/html-visual erd schema.prisma
/html-visual chart monthly revenue 2024

# Omit the type — it's inferred from context
/html-visual diagram the user signup flow

# Point at an existing output to revise it
/html-visual erd-orders.html add the refunds table
```

## How it works

1. Determines the visualization type from the first word, or infers it from the request. If it can't infer, it asks.
2. Reads the input first when there is one — a file path gets analyzed (Prisma schema → ERD), an existing HTML file gets edited in place rather than regenerated.
3. Pulls in project context when the request calls for it. Wording like "our", "current", or "the project's" means it reads the actual code, schema, or API before drawing anything.
4. Generates a single HTML file with dark/light toggle, draggable nodes, and responsive layout.
5. Validates the result — unclosed tags, smart quotes in attributes, overlapping elements — and fixes what it finds.
6. Tells you the command to open it.

## Output

One self-contained HTML file in the project root, named `<type>-<subject>.html` — `mockup-login-form.html`, `erd-orders.html`, `flow-payment.html`. When the type had to be inferred, the prefix is `visual-`. Everything is inline; libraries come from a CDN, so charts and slides need a network connection on first open.
