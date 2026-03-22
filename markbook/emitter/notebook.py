from __future__ import annotations

import nbformat

from ..parser.nodes import (
    ASTNode,
    ChapterNode,
    CodeCellNode,
    DividerNode,
    FrontmatterNode,
    MarkdownNode,
    TocNode,
)

ACCENT_COLOR = "#2E86AB"

CHAPTER_STYLES = {
    2: {"font_size": "1.6em", "border_width": "4px", "padding": "10px", "color": ACCENT_COLOR},
    3: {"font_size": "1.3em", "border_width": "3px", "padding": "8px", "color": ACCENT_COLOR},
    4: {"font_size": "1.1em", "border_width": "0", "padding": "0", "color": "#555"},
}


def render_chapter(node: ChapterNode) -> str:
    style = CHAPTER_STYLES.get(node.level, CHAPTER_STYLES[4])
    anchor = f'<a id="{node.anchor}"></a>\n' if node.anchor else ""
    tag = f"h{node.level}"
    border = f"border-left: {style['border_width']} solid {style['color']}; " if style["border_width"] != "0" else ""
    padding = f"padding-left: {style['padding']}; " if style["padding"] != "0" else ""
    return (
        f"{anchor}"
        f"<{tag} style=\"color: {style['color']}; {border}{padding}"
        f"font-size: {style['font_size']};\">"
        f"{node.text}</{tag}>"
    )


def render_toc(node: TocNode) -> str:
    lines = ["## Gliederung", ""]
    prev_level = 1  # track nesting

    for h in node.headings:
        if h.level == 2:
            # Top-level: bold link
            lines.append(f"* **[{h.text}](#{h.anchor})**")
            prev_level = 2
        elif h.level == 3:
            # Sub-chapter: indented
            lines.append(f"    * [{h.text}](#{h.anchor})")
            prev_level = 3
        elif h.level == 4:
            # Section: double-indented
            lines.append(f"        * [{h.text}](#{h.anchor})")
            prev_level = 4

    return "\n".join(lines)


def render_divider() -> str:
    return (
        '<hr style="border: none; border-top: 2px solid #dee2e6; '
        'margin: 20px 0;">'
    )


def emit_notebook(ast: list[ASTNode]) -> nbformat.NotebookNode:
    nb = nbformat.v4.new_notebook()
    kernel = "python3"
    metadata: dict[str, str] = {}

    for node in ast:
        if isinstance(node, FrontmatterNode):
            kernel = node.kernel
            if node.title:
                metadata["title"] = node.title
            if node.author:
                metadata["author"] = node.author
            # Emit header cell with title and author
            header_lines = []
            if node.title:
                header_lines.append(f"# {node.title}")
            if node.author:
                header_lines.append("")
                header_lines.append(f"Name: {node.author}")
            if header_lines:
                nb.cells.append(nbformat.v4.new_markdown_cell(source="\n".join(header_lines)))
            continue

        if isinstance(node, ChapterNode):
            nb.cells.append(nbformat.v4.new_markdown_cell(source=render_chapter(node)))

        elif isinstance(node, CodeCellNode):
            nb.cells.append(nbformat.v4.new_code_cell(source=node.source))

        elif isinstance(node, TocNode):
            nb.cells.append(nbformat.v4.new_markdown_cell(source=render_toc(node)))

        elif isinstance(node, DividerNode):
            nb.cells.append(nbformat.v4.new_markdown_cell(source=render_divider()))

        elif isinstance(node, MarkdownNode):
            nb.cells.append(nbformat.v4.new_markdown_cell(source=node.content))

    # Set kernel metadata
    nb.metadata["kernelspec"] = {
        "display_name": kernel.capitalize(),
        "language": kernel.replace("3", ""),
        "name": kernel,
    }
    for k, v in metadata.items():
        nb.metadata[k] = v

    return nb
