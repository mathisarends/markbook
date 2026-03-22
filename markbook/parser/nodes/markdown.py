from dataclasses import dataclass
from typing import TYPE_CHECKING

import nbformat

from markbook.parser.nodes.base import Node
from markbook.parser.views import TokenKind

if TYPE_CHECKING:
    from markbook.parser.views import Token


@dataclass
class MarkdownNode(Node):
    TOKEN_KIND = TokenKind.MARKDOWN

    content: str

    @classmethod
    def from_token(cls, token: Token) -> MarkdownNode | None:
        if token.kind == cls.TOKEN_KIND:
            return cls(content=token.value)
        if token.kind == TokenKind.FENCED:
            lang = token.meta.get("language", "").lower()
            if lang:
                return cls(content=f"```{lang}\n{token.value}\n```")
            return cls(content=token.value)
        return None

    def render(self, nb: nbformat.NotebookNode) -> None:
        cells: list[nbformat.NotebookNode] = nb.cells
        cells.append(nbformat.v4.new_markdown_cell(source=self.content))
