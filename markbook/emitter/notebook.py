from __future__ import annotations

import nbformat

from ..parser.nodes import (
    ASTNode,
    CalloutNode,
    ChapterNode,
    CodeCellNode,
    DividerNode,
    FrontmatterNode,
    MarkdownNode,
    MetaBadgesNode,
    TocNode,
)

ACCENT_COLOR = "#2E86AB"
WARNING_COLOR = "#E67E22"
SUCCESS_COLOR = "#27AE60"
DANGER_COLOR = "#E74C3C"

CALLOUT_STYLES = {
    "note": {"color": ACCENT_COLOR, "icon": "ℹ️", "bg": "#EBF5FB"},
    "warning": {"color": WARNING_COLOR, "icon": "⚠️", "bg": "#FEF9E7"},
    "tip": {"color": SUCCESS_COLOR, "icon": "💡", "bg": "#EAFAF1"},
    "danger": {"color": DANGER_COLOR, "icon": "🚨", "bg": "#FDEDEC"},
}

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


def render_callout(node: CalloutNode) -> str:
    style = CALLOUT_STYLES[node.kind]
    return (
        f'<div style="background: {style["bg"]}; border-left: 4px solid {style["color"]}; '
        f'padding: 12px 16px; margin: 10px 0; border-radius: 4px;">\n'
        f'<strong style="color: {style["color"]};">{style["icon"]} '
        f"{node.kind.capitalize()}</strong><br/>\n"
        f"{node.content}\n"
        f"</div>"
    )


def render_toc(node: TocNode) -> str:
    lines = [
        '<div style="background: #f8f9fa; border: 1px solid #dee2e6; '
        'border-radius: 6px; padding: 16px 24px; margin: 10px 0;">',
        f'<h3 style="color: {ACCENT_COLOR}; margin-top: 0;">Table of Contents</h3>',
    ]

    # Group: level 2 = top-level, level 3 = nested
    in_sub = False
    for h in node.headings:
        if h.level == 2:
            if in_sub:
                lines.append("</ul>")
                in_sub = False
            lines.append(f'<li><a href="#{h.anchor}" style="color: {ACCENT_COLOR}; '
                         f'text-decoration: none; font-weight: bold;">{h.text}</a></li>')
        elif h.level == 3:
            if not in_sub:
                lines.append('<ul style="list-style-type: disc; padding-left: 20px;">')
                in_sub = True
            lines.append(f'<li><a href="#{h.anchor}" style="color: #555; '
                         f'text-decoration: none;">{h.text}</a></li>')
    if in_sub:
        lines.append("</ul>")

    # Wrap in outer list
    body = "\n".join(lines[2:])
    return (
        lines[0] + "\n" + lines[1] + "\n"
        '<ul style="list-style-type: none; padding-left: 0;">\n'
        + body + "\n</ul>\n</div>"
    )


def render_meta_badges(node: MetaBadgesNode) -> str:
    badges = []
    for key, value in node.fields.items():
        badges.append(
            f'<span style="background: {ACCENT_COLOR}; color: white; '
            f"padding: 4px 12px; border-radius: 16px; margin: 4px; "
            f'font-size: 0.85em; display: inline-block;">'
            f"<strong>{key}:</strong> {value}</span>"
        )
    return '<div style="margin: 10px 0;">' + "\n".join(badges) + "</div>"


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
            continue

        if isinstance(node, ChapterNode):
            nb.cells.append(nbformat.v4.new_markdown_cell(source=render_chapter(node)))

        elif isinstance(node, CodeCellNode):
            nb.cells.append(nbformat.v4.new_code_cell(source=node.source))

        elif isinstance(node, CalloutNode):
            nb.cells.append(nbformat.v4.new_markdown_cell(source=render_callout(node)))

        elif isinstance(node, TocNode):
            nb.cells.append(nbformat.v4.new_markdown_cell(source=render_toc(node)))

        elif isinstance(node, MetaBadgesNode):
            nb.cells.append(nbformat.v4.new_markdown_cell(source=render_meta_badges(node)))

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
