import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

import nbformat

from markbook.parser.nodes.base import Node
from markbook.parser.tokens import TokenKind

if TYPE_CHECKING:
    from markbook.parser.tokens import Token


@dataclass
class ChapterNode(Node):
    TOKEN_KIND = TokenKind.HEADING
    PATTERN = re.compile(r"^(#{2,4})\s+(.+)$")

    _ACCENT_COLOR = "#2E86AB"

    _STYLES = {
        2: {"font_size": "1.6em", "border_width": "4px", "padding": "10px", "color": _ACCENT_COLOR},
        3: {"font_size": "1.3em", "border_width": "3px", "padding": "8px",  "color": _ACCENT_COLOR},
        4: {"font_size": "1.1em", "border_width": "0",   "padding": "0",    "color": "#555"},
    }

    level: int
    text: str
    anchor: str | None = None

    @classmethod
    def from_token(cls, token: Token) -> ChapterNode | None:
        if token.kind != cls.TOKEN_KIND:
            return None
        return cls(
            level=token.meta["level"],
            text=token.value,
            anchor=token.meta.get("anchor"),
        )

    @staticmethod
    def _slugify(text: str) -> str:
        slug = text.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s]+", "-", slug)
        return slug

    def ensure_anchor(self) -> None:
        if not self.anchor:
            self.anchor = self._slugify(self.text)

    def render(self, nb: nbformat.NotebookNode) -> None:
        style = self._STYLES.get(self.level, self._STYLES[4])
        anchor = f'<a id="{self.anchor}"></a>\n' if self.anchor else ""
        tag = f"h{self.level}"
        border = f"border-left: {style['border_width']} solid {style['color']}; " if style["border_width"] != "0" else ""
        padding = f"padding-left: {style['padding']}; " if style["padding"] != "0" else ""
        html = (
            f"{anchor}"
            f'<{tag} style="color: {style["color"]}; {border}{padding}font-size: {style["font_size"]};">'
            f"{self.text}</{tag}>"
        )
        cells: list[nbformat.NotebookNode] = nb.cells
        cells.append(nbformat.v4.new_markdown_cell(source=html))
