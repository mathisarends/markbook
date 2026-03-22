# markbook — Implementation Plan

> **markbook** is a CLI tool that compiles a custom Markdown DSL into rich, styled Jupyter Notebooks (`.ipynb`).
> Write in plain Markdown, render beautifully in Jupyter.

---

## Project Structure

```
markbook/
├── markbook/
│   ├── __init__.py
│   ├── cli.py              # Typer CLI entrypoint
│   ├── compiler.py         # Orchestrates parse → transform → emit
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── lexer.py        # Line-by-line tokenizer
│   │   ├── nodes.py        # AST node dataclasses
│   │   └── parser.py       # Token stream → AST
│   ├── emitter/
│   │   ├── __init__.py
│   │   └── notebook.py     # AST → nbformat Notebook
│   └── watcher.py          # watchdog-based file watcher
├── pyproject.toml
└── README.md
```

---

## DSL Syntax Reference

The `.md` file starts with a YAML frontmatter block, followed by DSL-annotated Markdown.

### 1. Frontmatter (YAML)

```yaml
---
title: "Diabetes Risk Classification"
kernel: python3
author: "Mathis"
---
```

Supported keys:

- `title` — sets notebook metadata title
- `kernel` — kernel name (default: `python3`)
- `author` — injected as notebook metadata

---

### 2. Chapter Headings

Standard Markdown headings are transformed into styled HTML cells with colored left-border and anchor links.

```markdown
## 1. Business Understanding {#chapter1}

### 1.1 Projektkontext {#chap1_1}
```

`##` → top-level chapter (large accent border, full color)
`###` → sub-chapter (smaller accent, same color family)
`####` → section (subtle, no border)

The `{#id}` suffix is the anchor ID. It gets stripped from display and injected as `<a id="..."></a>`.

---

### 3. Code Cells

Fenced code blocks with a language tag become **code cells**:

````markdown
```python
import pandas as pd
df = pd.read_csv("data.csv")
df.head()
```
````

Fenced blocks with `text`, `output`, or no language tag become **raw/markdown cells**.

---

### 4. Callout Blocks

Custom fenced directives for styled info boxes:

````markdown
```note
Diabetes Typ 2 betrifft ca. 8% der deutschen Bevölkerung.
```

```warning
Klasse-Imbalance beachten: 88% negativ, 12% positiv.
```

```tip
Verwende F₂-Score statt Accuracy bei unbalancierten Datensätzen.
```
````

Supported types: `note`, `warning`, `tip`, `danger`

Each renders as a styled HTML markdown cell with colored left-border, icon prefix, and background.

---

### 5. Table of Contents

The special directive `[TOC]` on its own line auto-generates a styled HTML table of contents from all `##` and `###` headings found in the document.

```markdown
[TOC]
```

Output: a nested `<ul>` with anchor links, matching the example format from the project brief.

---

### 6. Metadata Badges

Inline metadata rendered as pill badges in a markdown cell:

```markdown
:::meta
dataset: Pima Indians Diabetes Dataset
rows: 768
features: 8
target: Outcome (binary)
:::
```

Renders as a horizontal row of styled `<span>` badges.

---

### 7. Section Divider

```markdown
---
```

A horizontal rule becomes a styled `<hr>` markdown cell (not a notebook cell separator).

---

### 8. Regular Markdown

Everything else (paragraphs, bold, italic, lists, tables, blockquotes) is passed through as-is into **markdown cells**.

---

## Implementation Steps

### Step 1 — `parser/nodes.py`

Define all AST node types as `@dataclass`:

```python
@dataclass
class FrontmatterNode:
    title: str
    kernel: str
    author: str

@dataclass
class ChapterNode:
    level: int          # 2, 3, or 4
    text: str
    anchor: str | None

@dataclass
class CodeCellNode:
    language: str
    source: str

@dataclass
class CalloutNode:
    kind: str           # note | warning | tip | danger
    content: str

@dataclass
class TocNode:
    pass                # placeholder; resolved after full parse

@dataclass
class MetaBadgesNode:
    fields: dict[str, str]

@dataclass
class MarkdownNode:
    content: str

ASTNode = FrontmatterNode | ChapterNode | CodeCellNode | CalloutNode | TocNode | MetaBadgesNode | MarkdownNode
```

---

### Step 2 — `parser/lexer.py`

A simple **line-by-line state machine**. No regex soup — use clear states:

```
States: NORMAL | IN_FRONTMATTER | IN_FENCED_CODE | IN_META_BLOCK
```

Rules:

- `---` at line 0 → enter `IN_FRONTMATTER`
- `---` closing frontmatter → emit raw YAML string, return to `NORMAL`
- ` ``` ` opening → check language tag, enter `IN_FENCED_CODE`
- ` ``` ` closing → emit fenced block token with language + body
- `:::meta` → enter `IN_META_BLOCK`
- `:::` closing meta → emit meta block token
- `[TOC]` → emit TOC token
- `^#{2,4} ` → emit heading token
- Anything else → accumulate into current markdown buffer

Emit tokens as simple dataclasses:

```python
@dataclass
class Token:
    kind: str   # FRONTMATTER | HEADING | FENCED | META | TOC | MARKDOWN
    value: str
    meta: dict  # e.g. {"level": 2, "anchor": "chapter1", "language": "python"}
```

---

### Step 3 — `parser/parser.py`

Consumes the token stream and returns `list[ASTNode]`.

Key logic:

- `FRONTMATTER` token → parse with `yaml.safe_load()` → `FrontmatterNode`
- `HEADING` token → extract level, text, anchor `{#id}` suffix → `ChapterNode`
- `FENCED` token:
  - language in `[python, bash, sql, r, julia]` → `CodeCellNode`
  - language in `[note, warning, tip, danger]` → `CalloutNode`
  - otherwise → `MarkdownNode` (raw fenced block)
- `META` token → parse `key: value` lines → `MetaBadgesNode`
- `TOC` token → `TocNode` (resolved later in compiler)
- `MARKDOWN` token → `MarkdownNode`

After full parse: resolve `TocNode` by scanning all `ChapterNode`s in the AST.

---

### Step 4 — `emitter/notebook.py`

Converts `list[ASTNode]` → `nbformat.NotebookNode`.

Use `nbformat.v4.new_notebook()`, `new_markdown_cell()`, `new_code_cell()`.

#### HTML templates per node type

**ChapterNode** (level 2):

```python
def render_chapter(node: ChapterNode) -> str:
    anchor = f'<a id="{node.anchor}"></a>' if node.anchor else ""
    return (
        f'{anchor}\n'
        f'<h2 style="color: #2E86AB; border-left: 4px solid #2E86AB; '
        f'padding-left: 10px;">{node.text}</h2>'
    )
```

**CalloutNode**:

```python
CALLOUT_STYLES = {
    "note":    {"color": "#2E86AB", "icon": "ℹ️",  "bg": "#EBF5FB"},
    "warning": {"color": "#E67E22", "icon": "⚠️",  "bg": "#FEF9E7"},
    "tip":     {"color": "#27AE60", "icon": "💡", "bg": "#EAFAF1"},
    "danger":  {"color": "#E74C3C", "icon": "🚨", "bg": "#FDEDEC"},
}
```

**TocNode** — render as nested `<ul>` with inline styles, using the pre-resolved heading list.

**MetaBadgesNode** — render as `<div>` with inline `<span>` pills per key-value pair.

**CodeCellNode** → `nbformat.v4.new_code_cell(source=node.source)`

**MarkdownNode** → `nbformat.v4.new_markdown_cell(source=node.content)`

Write notebook with:

```python
nbformat.write(nb, output_path, version=4)
```

---

### Step 5 — `compiler.py`

```python
def compile(input_path: Path, output_path: Path) -> None:
    source = input_path.read_text(encoding="utf-8")
    tokens = tokenize(source)           # lexer
    ast = parse(tokens)                 # parser
    notebook = emit_notebook(ast)       # emitter
    nbformat.write(notebook, output_path, version=4)
```

---

### Step 6 — `cli.py`

```python
import typer
app = typer.Typer()

@app.command()
def build(
    input: Path = typer.Argument(..., help="Path to .md file"),
    output: Path = typer.Option(None, help="Output .ipynb path"),
):
    ...

@app.command()
def watch(
    input: Path = typer.Argument(...),
    output: Path = typer.Option(None),
):
    ...
```

`build` → run `compiler.compile()` once, print success with Rich.
`watch` → start `watcher.py` loop, recompile on every save.

---

### Step 7 — `watcher.py`

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class MarkbookHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path == str(self.input_path):
            compile(self.input_path, self.output_path)
            # print success/error with Rich
```

---

### Step 8 — `pyproject.toml` CLI entrypoint

```toml
[project.scripts]
markbook = "markbook.cli:app"
```

---

## Color Palette for HTML Output

Use consistently across all rendered cells:

```python
ACCENT_COLOR = "#2E86AB"   # chapter headings, note callouts
WARNING_COLOR = "#E67E22"  # warnings
SUCCESS_COLOR = "#27AE60"  # tips
DANGER_COLOR = "#E74C3C"   # danger callouts
```

---

## Error Handling

- Unknown frontmatter keys → log warning with Rich, continue
- Unclosed fenced block → raise `MarkbookSyntaxError` with line number
- Missing anchor on heading used in TOC → generate slug from text (`"1. Business Understanding"` → `"1-business-understanding"`)
- `nbformat.validate()` failure → print full error, still write file

---

## Out of Scope (v1)

- Multi-file documents / imports
- Custom themes / color config
- PDF export
- nbconvert integration
