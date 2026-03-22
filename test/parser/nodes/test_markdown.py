import nbformat
import pytest

from markbook.parser.views import Token, TokenKind
from markbook.parser.nodes.markdown import MarkdownNode


class TestFromToken:
    def test_parses_markdown_token(self):
        token = Token(kind=TokenKind.MARKDOWN, value="Hello **world**")
        node = MarkdownNode.from_token(token)
        assert node is not None
        assert node.content == "Hello **world**"

    def test_parses_fenced_with_unknown_language(self):
        token = Token(kind=TokenKind.FENCED, value="some output", meta={"language": "text"})
        node = MarkdownNode.from_token(token)
        assert node is not None
        assert node.content == "```text\nsome output\n```"

    def test_parses_fenced_with_empty_language(self):
        token = Token(kind=TokenKind.FENCED, value="raw content", meta={"language": ""})
        node = MarkdownNode.from_token(token)
        assert node is not None
        assert node.content == "raw content"

    def test_rejects_wrong_token_kind(self):
        token = Token(kind=TokenKind.TOC)
        assert MarkdownNode.from_token(token) is None

    def test_rejects_heading_token(self):
        token = Token(kind=TokenKind.HEADING, value="Title", meta={"level": 2})
        assert MarkdownNode.from_token(token) is None


class TestRender:
    def test_renders_markdown_cell(self):
        nb = nbformat.v4.new_notebook()
        node = MarkdownNode(content="Some **bold** text")
        node.render(nb)
        assert len(nb.cells) == 1
        assert nb.cells[0].cell_type == "markdown"
        assert nb.cells[0].source == "Some **bold** text"
