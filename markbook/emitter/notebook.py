import nbformat

from markbook.parser.nodes import ASTNode, FrontmatterNode


def emit_notebook(ast: list[ASTNode]) -> nbformat.NotebookNode:
    nb = nbformat.v4.new_notebook()
    kernel = "python3"
    metadata: dict[str, str] = {}

    for node in ast:
        if isinstance(node, FrontmatterNode):
            kernel = node.kernel
            if node.title:
                metadata["title"] = node.title
            if node.author:
                metadata["author"] = node.author

        node.render(nb)

    nb.metadata["kernelspec"] = {
        "display_name": kernel.capitalize(),
        "language": kernel.replace("3", ""),
        "name": kernel,
    }
    for k, v in metadata.items():
        nb.metadata[k] = v

    return nb
