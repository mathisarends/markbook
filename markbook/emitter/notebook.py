import nbformat

from markbook.parser.nodes import ASTNode, FrontmatterNode


def emit_notebook(ast: list[ASTNode]) -> nbformat.NotebookNode:
    nb = nbformat.v4.new_notebook()

    _apply_metadata(nb, ast)

    for node in ast:
        node.render(nb)

    return nb


def _apply_metadata(nb: nbformat.NotebookNode, ast: list[ASTNode]) -> None:
    frontmatter = next((n for n in ast if isinstance(n, FrontmatterNode)), None)

    _KERNEL_LANGUAGE: dict[str, str] = {
        "python3": "python",
        "python": "python",
        "r": "r",
        "julia": "julia",
    }

    kernel = frontmatter.kernel if frontmatter else "python3"
    nb.metadata["kernelspec"] = {
        "display_name": kernel.capitalize(),
        "language": _KERNEL_LANGUAGE.get(kernel, kernel),
        "name": kernel,
    }
    
    if frontmatter:
        if frontmatter.title:
            nb.metadata["title"] = frontmatter.title
        if frontmatter.author:
            nb.metadata["author"] = frontmatter.author