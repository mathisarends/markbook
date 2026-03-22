import nbformat
import pytest

from markbook.parser.views import Token, TokenKind
from markbook.parser.nodes.frontmatter import FrontmatterNode


class TestFromToken:
    def test_parses_full_frontmatter(self):
        token = Token(
            kind=TokenKind.FRONTMATTER,
            value='title: "My Notebook"\nkernel: python3\nauthor: "Alice"',
        )
        node = FrontmatterNode.from_token(token)
        assert node is not None
        assert node.title == "My Notebook"
        assert node.kernel == "python3"
        assert node.author == "Alice"

    def test_defaults_for_missing_keys(self):
        token = Token(kind=TokenKind.FRONTMATTER, value="title: Test")
        node = FrontmatterNode.from_token(token)
        assert node is not None
        assert node.title == "Test"
        assert node.kernel == "python3"
        assert node.author == ""

    def test_empty_frontmatter(self):
        token = Token(kind=TokenKind.FRONTMATTER, value="")
        node = FrontmatterNode.from_token(token)
        assert node is not None
        assert node.title == ""
        assert node.kernel == "python3"
        assert node.author == ""

    def test_rejects_wrong_token_kind(self):
        token = Token(kind=TokenKind.HEADING, value="something")
        assert FrontmatterNode.from_token(token) is None


class TestRender:
    def test_renders_title_and_author(self):
        nb = nbformat.v4.new_notebook()
        node = FrontmatterNode(title="My Notebook", author="Alice")
        node.render(nb)
        assert len(nb.cells) == 1
        source = nb.cells[0].source
        assert "# My Notebook" in source
        assert "Name: Alice" in source

    def test_renders_title_only(self):
        nb = nbformat.v4.new_notebook()
        node = FrontmatterNode(title="My Notebook")
        node.render(nb)
        assert len(nb.cells) == 1
        assert "# My Notebook" in nb.cells[0].source
        assert "Name:" not in nb.cells[0].source

    def test_renders_nothing_when_empty(self):
        nb = nbformat.v4.new_notebook()
        node = FrontmatterNode()
        node.render(nb)
        assert len(nb.cells) == 0
