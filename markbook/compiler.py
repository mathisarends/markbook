from __future__ import annotations

from pathlib import Path

import nbformat

from .parser.lexer import tokenize
from .parser.parser import parse
from .emitter.notebook import emit_notebook


def compile(input_path: Path, output_path: Path) -> None:
    source = input_path.read_text(encoding="utf-8")
    tokens = tokenize(source)
    ast = parse(tokens)
    notebook = emit_notebook(ast)
    nbformat.write(notebook, str(output_path), version=4)
