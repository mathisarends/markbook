from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum, auto


class State(Enum):
    NORMAL = auto()
    IN_FRONTMATTER = auto()
    IN_FENCED_CODE = auto()
    IN_META_BLOCK = auto()


@dataclass
class Token:
    kind: str  # FRONTMATTER | HEADING | FENCED | META | TOC | DIVIDER | MARKDOWN
    value: str = ""
    meta: dict[str, object] = field(default_factory=dict)


_HEADING_RE = re.compile(r"^(#{2,4})\s+(.+)$")
_FENCE_RE = re.compile(r"^```(\w*)$")


class MarkbookSyntaxError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f"Line {line}: {message}")
        self.line = line


def tokenize(source: str) -> list[Token]:
    lines = source.split("\n")
    tokens: list[Token] = []
    state = State.NORMAL
    buffer: list[str] = []
    fence_lang = ""
    fence_start_line = 0

    def flush_markdown():
        text = "\n".join(buffer).strip()
        if text:
            tokens.append(Token(kind="MARKDOWN", value=text))
        buffer.clear()

    for i, line in enumerate(lines):
        if state == State.NORMAL:
            # Frontmatter opening — only at very start of file
            if line.strip() == "---" and i == 0:
                flush_markdown()
                state = State.IN_FRONTMATTER
                continue

            # Divider (--- not at start of file)
            if line.strip() == "---":
                flush_markdown()
                tokens.append(Token(kind="DIVIDER"))
                continue

            # Meta block opening
            if line.strip() == ":::meta":
                flush_markdown()
                state = State.IN_META_BLOCK
                continue

            # TOC directive
            if line.strip() == "[TOC]":
                flush_markdown()
                tokens.append(Token(kind="TOC"))
                continue

            # Fenced code block opening
            fence_match = _FENCE_RE.match(line)
            if fence_match:
                flush_markdown()
                fence_lang = fence_match.group(1)
                fence_start_line = i + 1
                state = State.IN_FENCED_CODE
                continue

            # Heading
            heading_match = _HEADING_RE.match(line)
            if heading_match:
                flush_markdown()
                level = len(heading_match.group(1))
                text = heading_match.group(2).strip()
                # Extract anchor {#id}
                anchor = None
                anchor_match = re.search(r"\{#(\S+)\}\s*$", text)
                if anchor_match:
                    anchor = anchor_match.group(1)
                    text = text[: anchor_match.start()].strip()
                tokens.append(Token(kind="HEADING", value=text, meta={"level": level, "anchor": anchor}))
                continue

            # Regular line — accumulate
            buffer.append(line)

        elif state == State.IN_FRONTMATTER:
            if line.strip() == "---":
                tokens.append(Token(kind="FRONTMATTER", value="\n".join(buffer)))
                buffer.clear()
                state = State.NORMAL
            else:
                buffer.append(line)

        elif state == State.IN_FENCED_CODE:
            if line.strip() == "```":
                tokens.append(Token(kind="FENCED", value="\n".join(buffer), meta={"language": fence_lang}))
                buffer.clear()
                state = State.NORMAL
            else:
                buffer.append(line)

        elif state == State.IN_META_BLOCK:
            if line.strip() == ":::":
                tokens.append(Token(kind="META", value="\n".join(buffer)))
                buffer.clear()
                state = State.NORMAL
            else:
                buffer.append(line)

    # Check for unclosed blocks
    if state == State.IN_FENCED_CODE:
        raise MarkbookSyntaxError("Unclosed fenced code block", fence_start_line)
    if state == State.IN_FRONTMATTER:
        raise MarkbookSyntaxError("Unclosed frontmatter block", 1)
    if state == State.IN_META_BLOCK:
        raise MarkbookSyntaxError("Unclosed meta block", 0)

    flush_markdown()
    return tokens
