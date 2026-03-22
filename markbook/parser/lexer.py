import re

from markbook.parser.tokens import MarkbookSyntaxError, State, Token, TokenKind
from markbook.parser.nodes.chapter import ChapterNode
from markbook.parser.nodes.code import CodeCellNode
from markbook.parser.nodes.divider import DividerNode
from markbook.parser.nodes.frontmatter import FrontmatterNode
from markbook.parser.nodes.toc import TocNode

_ANCHOR_PATTERN = re.compile(r"\{#(\S+)\}\s*$")


def tokenize(source: str) -> list[Token]:
    return _Tokenizer(source).run()


class _Tokenizer:
    def __init__(self, source: str) -> None:
        self._lines = source.split("\n")
        self._tokens: list[Token] = []
        self._state = State.NORMAL
        self._buffer: list[str] = []
        self._fence_lang = ""
        self._fence_start_line = 0

    def run(self) -> list[Token]:
        for i, line in enumerate(self._lines):
            match self._state:
                case State.NORMAL:           self._handle_normal(i, line)
                case State.IN_FRONTMATTER:   self._handle_frontmatter(line)
                case State.IN_FENCED_CODE:   self._handle_fenced_code(line)
        self._finalize()
        return self._tokens

    def _handle_normal(self, i: int, line: str) -> None:
        stripped = line.strip()

        if i == 0 and stripped == FrontmatterNode.MARKER:
            self._flush_markdown()
            self._state = State.IN_FRONTMATTER
        elif stripped == DividerNode.MARKER:
            self._flush_markdown()
            self._tokens.append(Token(kind=TokenKind.DIVIDER))
        elif stripped == TocNode.MARKER:
            self._flush_markdown()
            self._tokens.append(Token(kind=TokenKind.TOC))
        elif fence_match := CodeCellNode.FENCE_PATTERN.match(line):
            self._flush_markdown()
            self._fence_lang = fence_match.group(1)
            self._fence_start_line = i + 1
            self._state = State.IN_FENCED_CODE
        elif heading_match := ChapterNode.PATTERN.match(line):
            self._flush_markdown()
            self._tokens.append(self._make_heading_token(heading_match))
        else:
            self._buffer.append(line)

    def _handle_frontmatter(self, line: str) -> None:
        if line.strip() == FrontmatterNode.MARKER:
            self._tokens.append(Token(kind=TokenKind.FRONTMATTER, value="\n".join(self._buffer)))
            self._buffer.clear()
            self._state = State.NORMAL
        else:
            self._buffer.append(line)

    def _handle_fenced_code(self, line: str) -> None:
        if line.strip() == CodeCellNode.FENCE_CLOSE:
            self._tokens.append(Token(kind=TokenKind.FENCED, value="\n".join(self._buffer), meta={"language": self._fence_lang}))
            self._buffer.clear()
            self._state = State.NORMAL
        else:
            self._buffer.append(line)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _finalize(self) -> None:
        if self._state == State.IN_FENCED_CODE:
            raise MarkbookSyntaxError("Unclosed fenced code block", self._fence_start_line)
        if self._state == State.IN_FRONTMATTER:
            raise MarkbookSyntaxError("Unclosed frontmatter block", 1)
        self._flush_markdown()

    def _flush_markdown(self) -> None:
        text = "\n".join(self._buffer).strip()
        if text:
            self._tokens.append(Token(kind=TokenKind.MARKDOWN, value=text))
        self._buffer.clear()

    @staticmethod
    def _make_heading_token(match: re.Match) -> Token:
        level = len(match.group(1))
        text = match.group(2).strip()
        anchor = None
        if anchor_match := _ANCHOR_PATTERN.search(text):
            anchor = anchor_match.group(1)
            text = text[: anchor_match.start()].strip()
        return Token(kind=TokenKind.HEADING, value=text, meta={"level": level, "anchor": anchor})