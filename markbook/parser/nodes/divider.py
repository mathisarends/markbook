from dataclasses import dataclass
from typing import TYPE_CHECKING

import nbformat

from markbook.parser.nodes.base import Node
from markbook.parser.tokens import TokenKind

if TYPE_CHECKING:
    from markbook.parser.tokens import Token


@dataclass
class DividerNode(Node):
    TOKEN_KIND = TokenKind.DIVIDER
    MARKER = "---"

    @classmethod
    def from_token(cls, token: Token) -> DividerNode | None:
        if token.kind != cls.TOKEN_KIND:
            return None
        return cls()

    def render(self, nb: nbformat.NotebookNode) -> None:
        html = '<hr style="border: none; border-top: 2px solid #dee2e6; margin: 20px 0;">'
        cells: list[nbformat.NotebookNode] = nb.cells
        cells.append(nbformat.v4.new_markdown_cell(source=html))
