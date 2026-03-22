from dataclasses import dataclass, field
from enum import StrEnum


class State(StrEnum):
    NORMAL = "normal"
    IN_FRONTMATTER = "in_frontmatter"
    IN_FENCED_CODE = "in_fenced_code"


class TokenKind(StrEnum):
    FRONTMATTER = "frontmatter"
    HEADING = "heading"
    FENCED = "fenced"
    TOC = "toc"
    DIVIDER = "divider"
    MARKDOWN = "markdown"


@dataclass
class Token:
    kind: TokenKind
    value: str = ""
    meta: dict[str, object] = field(default_factory=dict)


class MarkbookSyntaxError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f"Line {line}: {message}")
        self.line = line
