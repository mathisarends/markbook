from dataclasses import dataclass
from typing import TYPE_CHECKING

import nbformat
import yaml

from markbook.parser.nodes.base import Node
from markbook.parser.views import TokenKind

if TYPE_CHECKING:
    from markbook.parser.views import Token


@dataclass
class FrontmatterNode(Node):
    TOKEN_KIND = TokenKind.FRONTMATTER
    MARKER = "---"

    title: str = ""
    kernel: str = "python3"
    author: str = ""

    @classmethod
    def from_token(cls, token: Token) -> FrontmatterNode | None:
        if token.kind != cls.TOKEN_KIND:
            return None
        data = yaml.safe_load(token.value) or {}
        return cls(
            title=data.get("title", ""),
            kernel=data.get("kernel", "python3"),
            author=data.get("author", ""),
        )

    def render(self, nb: nbformat.NotebookNode) -> None:
        header_lines: list[str] = []
        if self.title:
            header_lines.append(f"# {self.title}")
        if self.author:
            header_lines.append("")
            header_lines.append(f"Name: {self.author}")
        if header_lines:
            cells: list[nbformat.NotebookNode] = nb.cells
            cells.append(nbformat.v4.new_markdown_cell(source="\n".join(header_lines)))
