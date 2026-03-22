from __future__ import annotations

import re

import yaml

from .lexer import Token
from .nodes import (
    ASTNode,
    ChapterNode,
    CodeCellNode,
    DividerNode,
    FrontmatterNode,
    MarkdownNode,
    TocNode,
)

CODE_LANGUAGES = {"python", "bash", "sql", "r", "julia", "sh", "javascript", "typescript", "java", "c", "cpp", "go", "rust"}


def _slugify(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug)
    return slug


def parse(tokens: list[Token]) -> list[ASTNode]:
    nodes: list[ASTNode] = []

    for token in tokens:
        if token.kind == "FRONTMATTER":
            data = yaml.safe_load(token.value) or {}
            nodes.append(FrontmatterNode(
                title=data.get("title", ""),
                kernel=data.get("kernel", "python3"),
                author=data.get("author", ""),
            ))

        elif token.kind == "HEADING":
            nodes.append(ChapterNode(
                level=token.meta["level"],
                text=token.value,
                anchor=token.meta.get("anchor"),
            ))

        elif token.kind == "FENCED":
            lang = token.meta.get("language", "").lower()
            if lang in CODE_LANGUAGES:
                nodes.append(CodeCellNode(language=lang, source=token.value))
            else:
                # Raw fenced block → markdown cell
                if lang:
                    nodes.append(MarkdownNode(content=f"```{lang}\n{token.value}\n```"))
                else:
                    nodes.append(MarkdownNode(content=token.value))

        elif token.kind == "TOC":
            nodes.append(TocNode())

        elif token.kind == "DIVIDER":
            nodes.append(DividerNode())

        elif token.kind == "MARKDOWN":
            nodes.append(MarkdownNode(content=token.value))

    # Resolve TOC nodes — fill in headings from all ChapterNodes
    chapter_nodes = [n for n in nodes if isinstance(n, ChapterNode)]
    # Ensure all chapters have anchors
    for ch in chapter_nodes:
        if not ch.anchor:
            ch.anchor = _slugify(ch.text)

    for node in nodes:
        if isinstance(node, TocNode):
            node.headings = list(chapter_nodes)

    return nodes
