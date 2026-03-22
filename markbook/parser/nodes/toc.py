from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import nbformat

from markbook.parser.nodes.base import Node
from markbook.parser.tokens import TokenKind

if TYPE_CHECKING:
    from markbook.parser.tokens import Token
    from markbook.parser.nodes.chapter import ChapterNode


@dataclass
class TocNode(Node):
    TOKEN_KIND = TokenKind.TOC
    MARKER = "[TOC]"

    headings: list[ChapterNode] = field(default_factory=list)

    @classmethod
    def from_token(cls, token: Token) -> TocNode | None:
        if token.kind != cls.TOKEN_KIND:
            return None
        return cls()

    def resolve(self, chapters: list[ChapterNode]) -> None:
        self.headings = list(chapters)

    def render(self, nb: nbformat.NotebookNode) -> None:
        lines = ["## Gliederung", ""]
        for h in self.headings:
            if h.level == 2:
                lines.append(f"* **[{h.text}](#{h.anchor})**")
            elif h.level == 3:
                lines.append(f"    * [{h.text}](#{h.anchor})")
            elif h.level == 4:
                lines.append(f"        * [{h.text}](#{h.anchor})")
        cells: list[nbformat.NotebookNode] = nb.cells
        cells.append(nbformat.v4.new_markdown_cell(source="\n".join(lines)))
