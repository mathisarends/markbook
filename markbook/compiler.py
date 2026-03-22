
from pathlib import Path

import nbformat

from markbook.parser import Parser, Tokenizer
from markbook.emitter.notebook import emit_notebook


def compile(input_path: Path, output_path: Path) -> None:
    source = input_path.read_text(encoding="utf-8")

    tokenizer = Tokenizer(source)
    tokens = tokenizer.run()

    parser = Parser(tokens)
    ast = parser.parse(

    )
    notebook = emit_notebook(ast)
    nbformat.write(notebook, str(output_path), version=4)
