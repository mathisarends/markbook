# markbook

A CLI tool that compiles a custom Markdown DSL into styled Jupyter Notebooks (`.ipynb`).
Write in plain Markdown, render beautifully in Jupyter.

## Installation

```bash
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

Standard Markdown headings with optional anchor IDs:

```markdown
## 1. Chapter Title {#chapter1}

### 1.1 Sub-chapter {#chap1_1}

#### 1.1.1 Section {#chap1_1_1}
```

`##` headings get a colored left border, `###` a subtler one, `####` no border.

### Table of Contents

Place `[TOC]` on its own line to auto-generate a linked table of contents from all headings:

```markdown
[TOC]
```

Renders as a markdown list with bold top-level links and indented sub-items.

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
