from markbook.parser.nodes.base import Node

from markbook.parser.nodes.chapter import ChapterNode
from markbook.parser.nodes.code import CodeCellNode
from markbook.parser.nodes.divider import DividerNode
from markbook.parser.nodes.frontmatter import FrontmatterNode
from markbook.parser.nodes.markdown import MarkdownNode
from markbook.parser.nodes.toc import TocNode

NODE_TYPES: list[Node] = [
    FrontmatterNode,
    ChapterNode,
    CodeCellNode,
    TocNode,
    DividerNode,
    MarkdownNode,
]

type ASTNode = FrontmatterNode | ChapterNode | CodeCellNode | TocNode | DividerNode | MarkdownNode