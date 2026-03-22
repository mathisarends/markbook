import nbformat
import pytest

from markbook.parser.tokens import Token, TokenKind
from markbook.parser.nodes.divider import DividerNode


class TestFromToken:
    def test_parses_divider_token(self):
        token = Token(kind=TokenKind.DIVIDER)
        node = DividerNode.from_token(token)
        assert node is not None

    def test_rejects_wrong_token_kind(self):
        token = Token(kind=TokenKind.MARKDOWN, value="---")
        assert DividerNode.from_token(token) is None


class TestRender:
    def test_renders_styled_hr(self):
        nb = nbformat.v4.new_notebook()
        node = DividerNode()
        node.render(nb)
        assert len(nb.cells) == 1
        assert nb.cells[0].cell_type == "markdown"
        assert "<hr" in nb.cells[0].source
        assert "border-top: 2px solid" in nb.cells[0].source
