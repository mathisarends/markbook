from .base import Node
from .chapter import ChapterNode
from .code import CodeCellNode
from .divider import DividerNode
from .frontmatter import FrontmatterNode
from .markdown import MarkdownNode
from .toc import TocNode

NODE_TYPES: list[type[Node]] = [
    FrontmatterNode,
    ChapterNode,
    CodeCellNode,
    TocNode,
    DividerNode,
    MarkdownNode,
]

type ASTNode = FrontmatterNode | ChapterNode | CodeCellNode | TocNode | DividerNode | MarkdownNode

__all__ = [
    "ASTNode",
    "NODE_TYPES",
    "Node",
    "ChapterNode",
    "CodeCellNode",
    "DividerNode",
    "FrontmatterNode",
    "MarkdownNode",
    "TocNode",
]
