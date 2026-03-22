import nbformat
import pytest

from markbook.parser.views import Token, TokenKind
from markbook.parser.nodes.code import CodeCellNode


class TestFromToken:
    def test_parses_python_fenced_block(self):
        token = Token(
            kind=TokenKind.FENCED,
            value="import pandas as pd",
            meta={"language": "python"},
        )
        node = CodeCellNode.from_token(token)
        assert node is not None
        assert node.language == "python"
        assert node.source == "import pandas as pd"

    @pytest.mark.parametrize("lang", ["python", "bash", "sql", "r", "julia", "javascript", "go", "rust"])
    def test_accepts_known_languages(self, lang: str):
        token = Token(kind=TokenKind.FENCED, value="code", meta={"language": lang})
        assert CodeCellNode.from_token(token) is not None

    def test_rejects_unknown_language(self):
        token = Token(kind=TokenKind.FENCED, value="text", meta={"language": "note"})
        assert CodeCellNode.from_token(token) is None

    def test_rejects_empty_language(self):
        token = Token(kind=TokenKind.FENCED, value="text", meta={"language": ""})
        assert CodeCellNode.from_token(token) is None

    def test_rejects_wrong_token_kind(self):
        token = Token(kind=TokenKind.MARKDOWN, value="text")
        assert CodeCellNode.from_token(token) is None


class TestRender:
    def test_renders_code_cell(self):
        nb = nbformat.v4.new_notebook()
        node = CodeCellNode(language="python", source="print('hello')")
        node.render(nb)
        assert len(nb.cells) == 1
        assert nb.cells[0].cell_type == "code"
        assert nb.cells[0].source == "print('hello')"
