import nbformat
import pytest

from markbook.parser.views import Token, TokenKind
from markbook.parser.nodes.chapter import ChapterNode


class TestFromToken:
    def test_parses_heading_with_anchor(self):
        token = Token(
            kind=TokenKind.HEADING,
            value="1. Business Understanding",
            meta={"level": 2, "anchor": "chapter1"},
        )
        node = ChapterNode.from_token(token)
        assert node is not None
        assert node.level == 2
        assert node.text == "1. Business Understanding"
        assert node.anchor == "chapter1"

    def test_parses_heading_without_anchor(self):
        token = Token(
            kind=TokenKind.HEADING,
            value="Overview",
            meta={"level": 3, "anchor": None},
        )
        node = ChapterNode.from_token(token)
        assert node is not None
        assert node.level == 3
        assert node.anchor is None

    def test_rejects_wrong_token_kind(self):
        token = Token(kind=TokenKind.MARKDOWN, value="text")
        assert ChapterNode.from_token(token) is None


class TestEnsureAnchor:
    def test_generates_slug_when_no_anchor(self):
        node = ChapterNode(level=2, text="1. Business Understanding")
        node.ensure_anchor()
        assert node.anchor == "1-business-understanding"

    def test_preserves_existing_anchor(self):
        node = ChapterNode(level=2, text="Chapter", anchor="custom")
        node.ensure_anchor()
        assert node.anchor == "custom"

    def test_slugify_strips_special_chars(self):
        node = ChapterNode(level=2, text="Erfolgskriterien & Metrik (F₂-Score)")
        node.ensure_anchor()
        assert " " not in node.anchor
        assert node.anchor == "erfolgskriterien-metrik-f₂-score"


class TestRender:
    def test_level2_has_border(self):
        nb = nbformat.v4.new_notebook()
        node = ChapterNode(level=2, text="Title", anchor="ch1")
        node.render(nb)
        assert len(nb.cells) == 1
        source = nb.cells[0].source
        assert '<a id="ch1"></a>' in source
        assert "<h2" in source
        assert "border-left: 4px" in source

    def test_level3_has_smaller_border(self):
        nb = nbformat.v4.new_notebook()
        node = ChapterNode(level=3, text="Sub", anchor="sub1")
        node.render(nb)
        source = nb.cells[0].source
        assert "<h3" in source
        assert "border-left: 3px" in source

    def test_level4_has_no_border(self):
        nb = nbformat.v4.new_notebook()
        node = ChapterNode(level=4, text="Section", anchor="sec1")
        node.render(nb)
        source = nb.cells[0].source
        assert "<h4" in source
        assert "border-left" not in source

    def test_no_anchor_tag_when_anchor_is_none(self):
        nb = nbformat.v4.new_notebook()
        node = ChapterNode(level=2, text="Title")
        node.render(nb)
        assert '<a id="' not in nb.cells[0].source
