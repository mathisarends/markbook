from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FrontmatterNode:
    title: str = ""
    kernel: str = "python3"
    author: str = ""


@dataclass
class ChapterNode:
    level: int  # 2, 3, or 4
    text: str
    anchor: str | None = None


@dataclass
class CodeCellNode:
    language: str
    source: str


@dataclass
class CalloutNode:
    kind: str  # note | warning | tip | danger
    content: str


@dataclass
class TocNode:
    headings: list[ChapterNode] = field(default_factory=list)


@dataclass
class MetaBadgesNode:
    fields: dict[str, str]


@dataclass
class DividerNode:
    pass


@dataclass
class MarkdownNode:
    content: str


type ASTNode = FrontmatterNode | ChapterNode | CodeCellNode | CalloutNode | TocNode | MetaBadgesNode | DividerNode | MarkdownNode
