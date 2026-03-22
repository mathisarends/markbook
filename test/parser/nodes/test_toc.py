import nbformat
import pytest

from markbook.parser.views import Token, TokenKind
from markbook.parser.nodes.chapter import ChapterNode
from markbook.parser.nodes.toc import TocNode


class TestFromToken:
    def test_parses_toc_token(self):
        token = Token(kind=TokenKind.TOC)
        node = TocNode.from_token(token)
        assert node is not None
        assert node.headings == []

    def test_rejects_wrong_token_kind(self):
        token = Token(kind=TokenKind.MARKDOWN, value="[TOC]")
        assert TocNode.from_token(token) is None


class TestResolve:
    def test_resolve_stores_chapters(self):
        node = TocNode()
        chapters = [
            ChapterNode(level=2, text="Ch1", anchor="ch1"),
            ChapterNode(level=3, text="Sub1", anchor="sub1"),
        ]
        node.resolve(chapters)
        assert len(node.headings) == 2
        assert node.headings[0].text == "Ch1"

    def test_resolve_copies_list(self):
        node = TocNode()
        chapters = [ChapterNode(level=2, text="Ch1", anchor="ch1")]
        node.resolve(chapters)
        chapters.append(ChapterNode(level=2, text="Ch2", anchor="ch2"))
        assert len(node.headings) == 1


class TestRender:
    def test_renders_gliederung_heading(self):
        nb = nbformat.v4.new_notebook()
        node = TocNode()
        node.render(nb)
        assert "## Gliederung" in nb.cells[0].source

    def test_renders_level2_as_bold_links(self):
        nb = nbformat.v4.new_notebook()
        node = TocNode(headings=[ChapterNode(level=2, text="Chapter 1", anchor="ch1")])
        node.render(nb)
        assert "* **[Chapter 1](#ch1)**" in nb.cells[0].source

    def test_renders_level3_indented(self):
        nb = nbformat.v4.new_notebook()
        node = TocNode(headings=[ChapterNode(level=3, text="Sub 1", anchor="sub1")])
        node.render(nb)
        assert "    * [Sub 1](#sub1)" in nb.cells[0].source

    def test_renders_level4_double_indented(self):
        nb = nbformat.v4.new_notebook()
        node = TocNode(headings=[ChapterNode(level=4, text="Section", anchor="sec1")])
        node.render(nb)
        assert "        * [Section](#sec1)" in nb.cells[0].source

    def test_renders_nested_structure(self):
        nb = nbformat.v4.new_notebook()
        node = TocNode(headings=[
            ChapterNode(level=2, text="Ch1", anchor="ch1"),
            ChapterNode(level=3, text="Sub1.1", anchor="sub1_1"),
            ChapterNode(level=3, text="Sub1.2", anchor="sub1_2"),
            ChapterNode(level=2, text="Ch2", anchor="ch2"),
        ])
        node.render(nb)
        source = nb.cells[0].source
        lines = source.split("\n")
        assert lines[0] == "## Gliederung"
        assert "* **[Ch1](#ch1)**" in source
        assert "    * [Sub1.1](#sub1_1)" in source
        assert "    * [Sub1.2](#sub1_2)" in source
        assert "* **[Ch2](#ch2)**" in source
