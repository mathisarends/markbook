---
name: markbook
description: Generate well-structured Jupyter Notebooks by writing Markdown DSL files and compiling them with the markbook CLI
version: 0.1.0
---

# markbook — Generate Jupyter Notebooks from Markdown

You are using **markbook**, a CLI that compiles a Markdown DSL into styled Jupyter Notebooks (`.ipynb`). Your workflow is: write a `.md` file using markbook's DSL syntax, then compile it.

## Workflow

### 1. Write the `.md` file

Create a Markdown file using markbook's DSL. See [SYNTAX.md](SYNTAX.md) for the complete reference.

### 2. Compile to notebook

```bash
markbook build <file>.md                # outputs <file>.ipynb
markbook build <file>.md -o output.ipynb  # custom output path
```

That's it. There are only two commands: `build` and `watch` (auto-rebuild on save).

## How to Structure a Good Notebook

When generating a `.md` file for markbook, follow this structure:

### Start with frontmatter

Always begin the file with YAML frontmatter:

```yaml
---
title: "Descriptive Title"
kernel: python3
author: "Author Name"
---
```

### Add a table of contents

Place `[TOC]` right after frontmatter for navigable notebooks. It auto-generates from all headings.

### Use `---` dividers between major sections

Dividers create visual separation. Place them between top-level chapters.

### Structure with `##`, `###`, `####` headings

Use heading levels consistently:

- `##` — top-level chapters (e.g., `## 1. Data Loading`)
- `###` — sub-sections (e.g., `### 1.1 Import Libraries`)
- `####` — minor sections when needed

Always add anchor IDs to headings for TOC links: `## Title {#anchor_id}`

### Alternate prose and code

Good notebooks explain what the code does **before** the code cell. Write a markdown paragraph or bullet list, then the code block:

```markdown
### 2.1 Load the Dataset {#load_data}

We load the CSV and inspect the first rows.

\`\`\`python
import pandas as pd
df = pd.read_csv("data.csv")
df.head()
\`\`\`
```

### Use recognized languages for code cells

Only these language tags produce code cells:
`python`, `bash`, `sql`, `r`, `julia`, `sh`, `javascript`, `typescript`, `java`, `c`, `cpp`, `go`, `rust`

Any other tag (or no tag) creates a markdown cell — useful for showing example output or pseudocode.

## Full Template

Here is a template for a data science notebook:

```markdown
---
title: "Project Title"
kernel: python3
author: "Your Name"
---

[TOC]

---

## 1. Introduction {#intro}

Brief description of the project goal.

- Objective 1
- Objective 2

---

## 2. Data Loading {#data}

### 2.1 Imports {#imports}

\`\`\`python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
\`\`\`

### 2.2 Read Data {#read_data}

\`\`\`python
df = pd.read_csv("data.csv")
print(f"Shape: {df.shape}")
df.head()
\`\`\`

---

## 3. Exploratory Analysis {#eda}

### 3.1 Overview {#overview}

\`\`\`python
df.describe()
\`\`\`

### 3.2 Visualizations {#viz}

\`\`\`python
fig, ax = plt.subplots(figsize=(8, 5))

# plotting code

plt.show()
\`\`\`

---

## 4. Modeling {#modeling}

### 4.1 Train/Test Split {#split}

\`\`\`python
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
\`\`\`

---

## 5. Evaluation {#eval}

\`\`\`python
from sklearn.metrics import classification_report
print(classification_report(y_test, y_pred))
\`\`\`
```

## Common Mistakes to Avoid

- **Missing frontmatter** — always start with `---` on line 1. Without it, no title/kernel metadata.
- **Using `#` (h1)** — single `#` is NOT recognized as a chapter. Use `##` and below.
- **Forgetting anchor IDs** — without `{#id}`, TOC links still work (auto-slugified), but explicit anchors are cleaner.
- **Unclosed code fences** — every ` ``` ` must have a matching closing ` ``` `. Unclosed blocks cause a build error.
- **Wrong language tag** — `\`\`\`py`does not work, use`\`\`\`python`. Tags are matched exactly against the supported list.
- **`---` on line 0** — the first `---` in the file always opens frontmatter, not a divider. Dividers only work after frontmatter.
