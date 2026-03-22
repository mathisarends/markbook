import re
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING

import nbformat

from markbook.parser.nodes.base import Node
from markbook.parser.views import TokenKind

if TYPE_CHECKING:
    from markbook.parser.views import Token


class _CodeLanguage(StrEnum):
    PYTHON = "python"
    BASH = "bash"
    SQL = "sql"
    R = "r"
    JULIA = "julia"
    SH = "sh"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    C = "c"
    CPP = "cpp"
    GO = "go"
    RUST = "rust"


@dataclass
class CodeCellNode(Node):
    TOKEN_KIND = TokenKind.FENCED
    FENCE_PATTERN = re.compile(r"^```(\w*)$")
    FENCE_CLOSE = "```"

    language: _CodeLanguage
    source: str

    @classmethod
    def from_token(cls, token: Token) -> CodeCellNode | None:
        if token.kind != cls.TOKEN_KIND:
            return None
        try:
            language = _CodeLanguage(token.meta.get("language", "").lower())
        except ValueError:
            return None
        return cls(language=language, source=token.value)

    def render(self, nb: nbformat.NotebookNode) -> None:
        cells: list[nbformat.NotebookNode] = nb.cells
        cells.append(nbformat.v4.new_code_cell(source=self.source))
