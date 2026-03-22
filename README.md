# markbook

A CLI tool that compiles a custom Markdown DSL into styled Jupyter Notebooks (`.ipynb`).
Write in plain Markdown, render beautifully in Jupyter.

## Installation

```bash
# From PyPI
pip install markbook

# Or as a CLI tool via uv (recommended)
uv tool install markbook

# For development
pip install -e .
```

## Usage

### Build a notebook

```bash
markbook build notebook.md
markbook build notebook.md -o output.ipynb
```

### Watch for changes

```bash
markbook watch notebook.md
```

Recompiles automatically on every save.

## DSL Syntax

### Frontmatter

YAML block at the top of the file. Renders as a title heading and author name in the first cell.

```yaml
---
title: "My Notebook"
kernel: python3
author: "Your Name"
---
```

### Headings

Use `##`, `###` and `####` to structure your notebook into chapters and sections. Each heading becomes its own styled markdown cell. Optional anchor IDs enable linking from the table of contents.

```markdown
## 1. Business Understanding {#chapter1}

### 1.1 Project Context {#chap1_1}

#### 1.1.1 Goals {#chap1_1_1}
```

| Level  | Rendered Style                                     |
|--------|----------------------------------------------------|
| `##`   | Large (1.6em), accent color `#2E86AB`, 4px left border |
| `###`  | Medium (1.3em), accent color `#2E86AB`, 3px left border |
| `####` | Small (1.1em), muted color `#555`, no border       |

Anchor IDs (`{#id}`) are optional — if omitted, markbook auto-generates them by slugifying the heading text.

> **Note:** `#` (h1) is **not** recognized as a chapter heading. It passes through as regular markdown. Use `##` and below.

### Table of Contents

Place `[TOC]` on its own line to auto-generate a linked table of contents from all headings in the document:

```markdown
[TOC]
```

This produces a cell like:

```
## Gliederung

* **[1. Business Understanding](#chapter1)**
    * [1.1 Project Context](#chap1_1)
        * [1.1.1 Goals](#chap1_1_1)
* **[2. Data Loading](#chapter2)**
    * [2.1 Imports](#chap2_1)
```

`##` headings become bold top-level entries, `###` are indented, `####` double-indented. All entries link to their heading's anchor ID.

### Code Cells

Fenced code blocks with a recognized language tag become notebook code cells:

````markdown
```python
import pandas as pd
df = pd.read_csv("data.csv")
```
````

Supported languages: `python`, `bash`, `sql`, `r`, `julia`, `sh`, `javascript`, `typescript`, `java`, `c`, `cpp`, `go`, `rust`.

Fenced blocks with other or no language tags become markdown cells.

### Section Dividers

A horizontal rule becomes a styled `<hr>`:

```markdown
---
```

### Regular Markdown

Everything else (paragraphs, bold, italic, lists, tables, blockquotes) passes through as-is into markdown cells.

## Example

See [`examples/diabetes.md`](examples/diabetes.md) for a full example. Build it with:

```bash
markbook build examples/diabetes.md
```

## Dependencies

- [nbformat](https://github.com/jupyter/nbformat) - Jupyter notebook format
- [PyYAML](https://pyyaml.org/) - YAML frontmatter parsing
- [Typer](https://typer.tiangolo.com/) - CLI framework
- [Rich](https://rich.readthedocs.io/) - Terminal output
- [watchdog](https://github.com/gorakhargosh/watchdog) - File watching
